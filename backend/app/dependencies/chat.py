from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.llm.service import LLMService
from app.prompts.builder import PromptBuilder
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_citation_repository import MessageCitationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.retrieval.service import RetrievalService
from app.services.chat.chat_service import ChatService
from app.services.chat.conversation_service import ConversationService


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    """
    Dependency injection provider for ConversationService.
    """
    conversation_repo = ConversationRepository(db)
    workspace_repo = WorkspaceRepository(db)
    return ConversationService(
        conversation_repo=conversation_repo,
        workspace_repo=workspace_repo,
    )


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """
    Dependency injection provider for ChatService, orchestrating the entire RAG pipeline.
    """
    conversation_service = get_conversation_service(db)
    message_repo = MessageRepository(db)
    citation_repo = MessageCitationRepository(db)
    retrieval_service = RetrievalService(db)
    prompt_builder = PromptBuilder()
    llm_service = LLMService(provider_type="gemini")
    conversation_repo = ConversationRepository(db)
    
    return ChatService(
        conversation_service=conversation_service,
        message_repo=message_repo,
        citation_repo=citation_repo,
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
        conversation_repo=conversation_repo,
    )
