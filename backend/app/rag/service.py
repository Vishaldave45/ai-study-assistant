import time
import logging
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.workspace_repository import WorkspaceRepository
from app.rag.orchestrator import RAGOrchestrator
from app.rag.exceptions import NoContextFound, WorkspaceNotFound, RAGException
from app.rag.schemas import AnswerResponse

logger = logging.getLogger(__name__)


class RAGService:

    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = RAGOrchestrator(db)

    def query(self, workspace_id: UUID, question: str, current_user_id: UUID) -> AnswerResponse:
        """
        Validates ownership, validates query input, measures execution time,
        and executes the orchestrator.
        """
        # Validate Workspace owner permission
        workspaces = WorkspaceRepository(self.db)
        workspace = workspaces.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFound(f"Workspace with ID {workspace_id} not found.")

        if workspace.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can access this workspace.",
            )

        # Enforce question validation
        if not question or not question.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Question cannot be empty.",
            )

        # Run with latency measurement
        start_time = time.perf_counter()
        try:
            logger.info(f"RAGService: executing query for question '{question}' in workspace {workspace_id}")
            result = self.orchestrator.query(workspace_id, question)
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)

            return AnswerResponse(
                answer=result["answer"],
                citations=result["citations"],
                chunks_used=result["chunks_used"],
                model=result["model"],
                processing_time_ms=processing_time_ms,
            )
        except NoContextFound:
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info("RAGService: No context found, returning fallback response DTO.")
            return AnswerResponse(
                answer="I couldn't find relevant information in your uploaded documents.",
                citations=[],
                chunks_used=0,
                model="gemini-2.5-flash",
                processing_time_ms=processing_time_ms,
            )
