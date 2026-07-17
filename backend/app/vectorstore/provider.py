from abc import ABC, abstractmethod
from uuid import UUID
from app.vectorstore.schemas import SearchResult


class VectorStoreProvider(ABC):

    @abstractmethod
    def create(self, workspace_id: UUID) -> None:
        """Create a new, empty index for the workspace in memory."""
        pass

    @abstractmethod
    def load(self, workspace_id: UUID) -> None:
        """Load the index and metadata for the workspace from disk."""
        pass

    @abstractmethod
    def save(self, workspace_id: UUID) -> None:
        """Save the index and metadata for the workspace to disk."""
        pass

    @abstractmethod
    def add(
        self,
        workspace_id: UUID,
        vectors: list[list[float]],
        metadata: list[dict],
    ) -> None:
        """Add vectors and their associated metadata mapping to the workspace index."""
        pass

    @abstractmethod
    def search(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Perform similarity search on the workspace index using the query vector."""
        pass

    @abstractmethod
    def delete(self, workspace_id: UUID, document_id: UUID) -> None:
        """Delete all vectors and metadata mapping belonging to a specific document in the workspace."""
        pass

    @abstractmethod
    def reset(self, workspace_id: UUID) -> None:
        """Clear all vectors and metadata mapping for the workspace index."""
        pass
