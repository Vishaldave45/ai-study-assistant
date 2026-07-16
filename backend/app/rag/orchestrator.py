from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.models.document import Document
from app.database.enums import DocumentStatus
from app.vectorstore.faiss_store import FAISSVectorStore
from app.repositories.workspace_repository import WorkspaceRepository
from app.rag.pipeline import RAGPipeline
from app.rag.exceptions import RAGException, WorkspaceNotFound


class RAGOrchestrator:

    def __init__(self, db: Session):
        self.db = db
        self.pipeline = RAGPipeline(db)

    def query(self, workspace_id: UUID, question: str) -> dict:
        """
        Validates the workspace state and runs the RAG query pipeline.
        """
        # Validate workspace existence and presence of indexed documents
        self.validate_workspace(workspace_id)

        # Run query pipeline
        return self.pipeline.answer_question(workspace_id, question)

    def validate_workspace(self, workspace_id: UUID) -> None:
        """
        Airtight pre-flight check:
        1. Checks if workspace exists in the DB.
        2. Checks if there are any documents with status == READY in this workspace.
        3. Checks if the FAISS index files exist on disk for the workspace.
        """
        workspaces = WorkspaceRepository(self.db)
        workspace = workspaces.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFound(f"Workspace with ID {workspace_id} not found.")

        # Check for READY documents
        stmt = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.status == DocumentStatus.READY,
        )
        docs = self.db.execute(stmt).scalars().all()

        # Check for index existence on disk
        store = FAISSVectorStore()
        if not docs or not store.index_exists(workspace_id):
            raise RAGException("No indexed documents found.")
