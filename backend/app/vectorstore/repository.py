from uuid import UUID
from sqlalchemy.orm import Session
from app.vectorstore.faiss_store import FAISSVectorStore
from app.vectorstore.schemas import SearchResult


class VectorStoreRepository:

    def __init__(self, db: Session | None = None):
        self.db = db
        self.store = FAISSVectorStore()

    def get_index(self, workspace_id: UUID) -> None:
        self.store.load(workspace_id)

    def add_vectors(
        self,
        workspace_id: UUID,
        vectors: list[list[float]],
        metadata: list[dict],
    ) -> None:
        self.store.add(workspace_id, vectors, metadata)
        self.store.save(workspace_id)

    def search_vectors(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        return self.store.search(workspace_id, query_vector, top_k)

    def delete_document_vectors(self, workspace_id: UUID, document_id: UUID) -> None:
        self.store.delete(workspace_id, document_id)
        self.store.save(workspace_id)

    def reset_workspace_index(self, workspace_id: UUID) -> None:
        self.store.reset(workspace_id)
        self.store.save(workspace_id)
