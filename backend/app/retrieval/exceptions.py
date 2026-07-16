class RetrievalError(Exception):
    """Base exception for all retrieval operations."""

    pass


class RetrieverConfigError(RetrievalError):
    """Raised when retriever configuration is invalid."""

    pass


class QueryEmbeddingError(RetrievalError):
    """Raised when query embedding generation fails."""

    pass
