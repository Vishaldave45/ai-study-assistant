import time
import json
import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.enums import DocumentStatus
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.document_repository import DocumentRepository
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
from app.retrieval.service import RetrievalService
from app.llm.service import LLMService
from app.prompts.explain.builder import ExplainPromptBuilder
from app.schemas.explain.request import ExplainRequest
from app.schemas.explain.response import ExplainResponse

logger = logging.getLogger(__name__)


class ExplainService:
    """
    Orchestrates targeted concept explanation generation: runs semantic search across
    workspace document chunks, compiles the level-specific prompt, and parses the structured JSON LLM output.
    """

    def __init__(self, db: Session):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.retrieval_service = RetrievalService(db)
        self.llm_service = LLMService(provider_type="gemini")
        self.prompt_builder = ExplainPromptBuilder()

    def explain_concept(
        self,
        workspace_id: UUID,
        current_user_id: UUID,
        request: ExplainRequest,
    ) -> ExplainResponse:
        """
        Retrieves semantic context for the concept, generates the structured explanation via Gemini,
        and parses it into an ExplainResponse DTO.
        """
        # 1. Validate Workspace existence and owner permission
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(f"Workspace with ID {workspace_id} not found.")

        if workspace.owner_id != current_user_id:
            raise WorkspaceAccessDeniedError("Access denied for this workspace.")

        # 2. Check for READY documents in the workspace
        documents = self.document_repo.list_by_workspace(workspace_id)
        ready_docs = [doc for doc in documents if doc.status == DocumentStatus.READY]
        if not ready_docs:
            raise ValueError("No indexed or processed documents found in this workspace to explain concepts from.")

        # 3. Retrieve matching context chunks via semantic search
        # We query for up to 15 chunks so that if we are filtering by document_id, we still get enough candidates
        retrieval = self.retrieval_service.retrieve(
            workspace_id=workspace_id,
            query=request.concept,
            top_k=15,
        )

        # 4. Filter chunks if document_id is specified
        retrieved_chunks = retrieval.chunks
        if request.document_id:
            # Validate document existence and workspace mapping
            document = self.document_repo.get_by_id(request.document_id)
            if not document:
                raise DocumentNotFoundError(f"Document with ID {request.document_id} not found.")
            if document.workspace_id != workspace_id:
                raise DocumentAccessDeniedError("Document does not belong to the specified workspace.")
            if document.status != DocumentStatus.READY:
                raise ValueError("Document is not ready (not indexed/processed).")

            target_doc_id_str = str(request.document_id)
            retrieved_chunks = [c for c in retrieved_chunks if c.document_id == target_doc_id_str]

        # 5. Format chunks for prompt builder
        chunks_for_builder = []
        for chunk in retrieved_chunks:
            filename = chunk.metadata.get("original_filename", "Unknown Document")
            # Page defaults to N/A if missing
            page_num = chunk.metadata.get("page_label", None)
            if page_num is None:
                page_num = chunk.page if getattr(chunk, "page", None) is not None else "N/A"
            
            chunks_for_builder.append(
                {
                    "content": chunk.text,
                    "filename": filename,
                    "page": str(page_num),
                }
            )

        # 6. Compile explanation prompt & invoke LLM
        start_time = time.perf_counter()

        prompt_str, chunk_count = self.prompt_builder.build(
            concept=request.concept,
            chunks=chunks_for_builder,
            level=request.level,
        )

        logger.info(
            f"ExplainService: Generating '{request.level}' explanation for concept '{request.concept}' "
            f"in workspace {workspace_id} using {chunk_count} chunks."
        )

        llm_response = self.llm_service.generate(prompt_str)
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # 7. Parse the structured JSON response
        parsed_data = self._clean_and_parse_json(llm_response.answer)

        # 8. Construct response DTO
        return ExplainResponse(
            explanation=parsed_data.get("explanation", ""),
            examples=parsed_data.get("examples", []),
            important_points=parsed_data.get("important_points", []),
            references=parsed_data.get("references", []),
            follow_up_questions=parsed_data.get("follow_up_questions", []),
            processing_time_ms=processing_time_ms,
            model=llm_response.model,
        )

    def _clean_and_parse_json(self, text: str) -> dict:
        """
        Cleans markdown wrapper ticks (if any) and parses the raw JSON string safely.
        Falls back gracefully if the LLM fails to return valid JSON.
        """
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error(f"ExplainService: Failed to parse LLM response as JSON: {exc}. Text: {text}")
            # Fallback wrapper
            return {
                "explanation": text,
                "examples": [],
                "important_points": [],
                "references": [],
                "follow_up_questions": [],
            }
