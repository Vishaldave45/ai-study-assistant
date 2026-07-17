class VectorStoreError(Exception):
    """Base exception for all vector store operations."""

    pass


class IndexNotFoundError(VectorStoreError):
    """Raised when a workspace vector index cannot be found on disk."""

    pass


class DimensionMismatchError(VectorStoreError):
    """Raised when the vector dimension does not match the configured index dimension."""

    pass


class SearchError(VectorStoreError):
    """Raised when similarity search fails."""

    pass
