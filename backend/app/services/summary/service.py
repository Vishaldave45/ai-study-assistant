import time
import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.enums import DocumentStatus
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
from app.llm.service import LLMService
from app.prompts.summary.builder import SummaryPromptBuilder
from app.schemas.summary.request import SummaryRequest
from app.schemas.summary.response import SummaryResponse

logger = logging.getLogger(__name__)


class SummaryService:
    """
    Handles summary generation orchestration, including validating workspace/document access,
    fetching READY text chunks, formatting the study prompts, and invoking the LLM.
    """

    def __init__(self, db: Session):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.llm_service = LLMService(provider_type="gemini")
        self.prompt_builder = SummaryPromptBuilder()

    def generate_summary(
        self,
        workspace_id: UUID,
        current_user_id: UUID,
        request: SummaryRequest,
    ) -> SummaryResponse:
        """
        Retrieves READY chunks, builds the prompt, calls LLM, and measures processing performance.
        """
        # 1. Validate Workspace existence and user access
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(f"Workspace with ID {workspace_id} not found.")

        if workspace.owner_id != current_user_id:
            raise WorkspaceAccessDeniedError("Access denied for this workspace.")

        # 2. Gather Document chunks
        chunks_for_builder = []

        if request.document_id:
            # Document-specific summary
            document = self.document_repo.get_by_id(request.document_id)
            if not document:
                raise DocumentNotFoundError(f"Document with ID {request.document_id} not found.")

            if document.workspace_id != workspace_id:
                raise DocumentAccessDeniedError("Document does not belong to the specified workspace.")

            if document.status != DocumentStatus.READY:
                raise ValueError("Document is not ready (not indexed/processed).")

            # Load chunks for this document
            chunks = self.chunk_repo.list_by_document(document.id)
            for c in chunks:
                chunks_for_builder.append(
                    {
                        "content": c.content,
                        "filename": document.original_filename,
                        "page": "N/A",
                    }
                )
        else:
            # Workspace-wide summary: gather from all READY documents
            documents = self.document_repo.list_by_workspace(workspace_id)
            ready_docs = [doc for doc in documents if doc.status == DocumentStatus.READY]

            if not ready_docs:
                raise ValueError("No indexed or processed documents found in this workspace to summarize.")

            for doc in ready_docs:
                chunks = self.chunk_repo.list_by_document(doc.id)
                for c in chunks:
                    chunks_for_builder.append(
                        {
                            "content": c.content,
                            "filename": doc.original_filename,
                            "page": "N/A",
                        }
                    )

        if not chunks_for_builder:
            raise ValueError("No text content found to summarize.")

        # 3. Compile prompt & invoke Gemini
        start_time = time.perf_counter()
        
        prompt_str, chunk_count = self.prompt_builder.build(
            chunks=chunks_for_builder,
            template_type=request.template_type,
        )

        logger.info(
            f"SummaryService: Requesting {request.template_type} summary "
            f"for workspace {workspace_id} using {chunk_count} chunks."
        )

        llm_response = self.llm_service.generate(prompt_str)

        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        return SummaryResponse(
            summary=llm_response.answer,
            token_usage=llm_response.usage,
            chunk_count=chunk_count,
            processing_time_ms=processing_time_ms,
            model=llm_response.model,
        )
