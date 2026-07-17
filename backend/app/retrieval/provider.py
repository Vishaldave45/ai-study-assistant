from abc import ABC, abstractmethod
from uuid import UUID
from app.vectorstore.schemas import SearchResult


class RetrieverProvider(ABC):

    @abstractmethod
    def retrieve(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        """Retrieve matches for the query vector in the workspace."""
        pass

    @abstractmethod
    def retrieve_with_scores(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        """Retrieve matches with scores for the query vector in the workspace."""
        pass

    @abstractmethod
    def retrieve_by_workspace(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        """Retrieve matches restricted to the workspace."""
        pass
