import logging
from uuid import UUID

from sqlalchemy import select

from app.database.enums import MessageRole
from app.database.models.document import Document
from app.database.models.message_citation import MessageCitation
from app.database.models.user import User
from app.llm.service import LLMService
from app.prompts.builder import PromptBuilder
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_citation_repository import MessageCitationRepository
from app.repositories.message_repository import MessageRepository
from app.retrieval.service import RetrievalService
from app.schemas.chat import (
    ChatResponse,
    CitationResponse,
    TokenUsageResponse,
)
from app.services.chat.conversation_service import ConversationService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestration layer coordinating all RAG workflows.
    Ensures separation of concerns by delegating retrieval, prompt compilation,
    and LLM invocation to their respective services.
    """

    def __init__(
        self,
        conversation_service: ConversationService,
        message_repo: MessageRepository,
        citation_repo: MessageCitationRepository,
        retrieval_service: RetrievalService,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
        conversation_repo: ConversationRepository,
    ):
        self.conversation_service = conversation_service
        self.message_repo = message_repo
        self.citation_repo = citation_repo
        self.retrieval_service = retrieval_service
        self.prompt_builder = prompt_builder
        self.llm_service = llm_service
        self.conversation_repo = conversation_repo
        self.db = message_repo.db

    def chat(
        self,
        conversation_id: UUID,
        question: str,
        current_user: User,
    ) -> ChatResponse:
        """
        Coordinates RAG sequence:
        1. Validate conversation active state and ownership
        2. Create and commit User message immediately (retaining it on LLM failure)
        3. Load chronological conversation memory
        4. Retrieve relevant chunks from FAISS
        5. Build prompt incorporating history and budget constraints
        6. Request LLM generation from Gemini
        7. Save Assistant message and Citations
        8. Auto-generate conversation title if default
        9. Return structured ChatResponse API DTO
        """
        # 1. Validate Conversation
        conversation = self.conversation_service.get_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        self.conversation_service.validate_can_message(conversation)

        # 2. Save User Message in its own transaction (retained on LLM failure)
        user_message = self.message_repo.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=question,
        )
        try:
            self.db.commit()
            self.db.refresh(user_message)
            # Update last_message_at
            self.conversation_service.touch_conversation(conversation_id)
        except Exception:
            self.db.rollback()
            raise

        # 3. Load Conversation Memory (last 10 messages, chronological order)
        memory_messages = self.message_repo.last_messages(
            conversation_id=conversation_id,
            limit=10,
        )
        memory_messages.reverse()

        # 4. Retrieval from Vectorstore
        retrieval = self.retrieval_service.retrieve(
            workspace_id=conversation.workspace_id,
            query=question,
        )

        # Format context chunks for builder using pre-resolved metadata
        chunks_for_builder = [
            {
                "content": res.text,
                "filename": res.metadata.get("original_filename", "Unknown Document"),
                "page": "N/A",
            }
            for res in retrieval.chunks
        ]

        # 5. Build Prompt
        prompt, num_chunks_used = self.prompt_builder.build_with_history(
            query=question,
            chunks=chunks_for_builder,
            history=memory_messages,
        )

        # 6. Gemini LLM Invocation
        logger.info(f"ChatService: Querying LLM for conversation {conversation_id}")
        llm_response = self.llm_service.generate(prompt)

        # 7. Save Assistant Message, Citations, and Title updates in a single transaction
        try:
            assistant_message = self.message_repo.create(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=llm_response.answer,
            )
            self.db.flush()

            # Prepare Citations
            citations_to_save = []
            for res in retrieval.chunks[:num_chunks_used]:
                chunk_id = UUID(res.chunk_id) if isinstance(res.chunk_id, str) else res.chunk_id
                citation = MessageCitation(
                    message_id=assistant_message.id,
                    document_chunk_id=chunk_id,
                )
                citations_to_save.append(citation)

            if citations_to_save:
                # Wrapped in nested transaction to tolerate citation failures gracefully
                try:
                    with self.db.begin_nested():
                        self.citation_repo.bulk_create(citations_to_save)
                except Exception as e:
                    logger.warning(
                        f"Failed to save citations for message {assistant_message.id}. Continuing. Error: {e}"
                    )

            # 8. Auto-generate Conversation Title if still default
            default_title = self.conversation_service.generate_default_title()
            if conversation.title == default_title:
                try:
                    title_prompt = (
                        "You are a helpful assistant.\n"
                        "Generate a extremely short, concise title (maximum 4 words, no quotes or markdown) "
                        "summarizing the following question:\n"
                        f"'{question}'"
                    )
                    title_response = self.llm_service.generate(title_prompt)
                    new_title = title_response.answer.strip().strip('"').strip("'").strip()
                    if new_title:
                        self.conversation_repo.rename(conversation, new_title[:255])
                except Exception as title_err:
                    logger.warning(
                        f"Failed to auto-generate conversation title for {conversation_id}: {title_err}"
                    )

            self.db.commit()
            self.db.refresh(assistant_message)
            # Touch conversation again for assistant response timestamp
            self.conversation_service.touch_conversation(conversation_id)

        except Exception as e:
            self.db.rollback()
            logger.exception(f"Database write failure during RAG persistence: {e}")
            raise

        # 9. Format response DTO
        citations_response = []
        for res in retrieval.chunks[:num_chunks_used]:
            doc_id = UUID(res.document_id) if isinstance(res.document_id, str) else res.document_id
            doc_name = res.metadata.get("original_filename", "Unknown Document")
            citations_response.append(
                CitationResponse(
                    document_id=doc_id,
                    document_name=doc_name,
                    page="N/A",
                    score=res.score,
                )
            )

        usage_response = self._map_usage(llm_response.usage)

        # Log completion
        logger.info(
            f"RAG Chat Completed. User: {current_user.id}, Conversation: {conversation_id}, Chunks Used: {num_chunks_used}"
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            answer=llm_response.answer,
            citations=citations_response,
            usage=usage_response,
        )

    def _map_usage(self, usage_dict: dict | None) -> TokenUsageResponse:
        """
        Maps dictionary representation of token usage metadata safely into the DTO.
        """
        if not usage_dict:
            return TokenUsageResponse(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            
        prompt = (
            usage_dict.get("prompt_tokens")
            or usage_dict.get("prompt_token_count")
            or 0
        )
        completion = (
            usage_dict.get("completion_tokens")
            or usage_dict.get("candidates_token_count")
            or usage_dict.get("completion_token_count")
            or 0
        )
        total = (
            usage_dict.get("total_tokens")
            or usage_dict.get("total_token_count")
            or 0
        )

        if total == 0 and (prompt > 0 or completion > 0):
            total = prompt + completion

        return TokenUsageResponse(
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
        )
