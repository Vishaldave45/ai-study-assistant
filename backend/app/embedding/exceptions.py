class EmbeddingError(Exception):
    """Base exception for all embedding-related errors."""

    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when there is an issue with the embedding model loading."""

    pass


class EmbeddingGenerationError(EmbeddingError):
    """Raised when vector generation fails."""

    pass
