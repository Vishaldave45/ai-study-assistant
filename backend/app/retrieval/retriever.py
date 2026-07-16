from uuid import UUID
from app.retrieval.provider import RetrieverProvider
from app.vectorstore.repository import VectorStoreRepository
from app.vectorstore.schemas import SearchResult


class FAISSRetriever(RetrieverProvider):

    def __init__(self, vector_repo: VectorStoreRepository):
        self.vector_repo = vector_repo

    def retrieve(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        return self.vector_repo.search_vectors(workspace_id, query_vector, top_k)

    def retrieve_with_scores(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        return self.vector_repo.search_vectors(workspace_id, query_vector, top_k)

    def retrieve_by_workspace(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        return self.vector_repo.search_vectors(workspace_id, query_vector, top_k)
