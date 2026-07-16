class RAGException(Exception):
    """Base exception for all RAG operations."""
    pass


class WorkspaceNotFound(RAGException):
    """Raised when the specified workspace cannot be found."""
    pass


class NoContextFound(RAGException):
    """Raised when no matching document context is found above the similarity threshold."""
    pass


class GenerationFailed(RAGException):
    """Raised when LLM text generation fails."""
    pass


class RetrieverFailed(RAGException):
    """Raised when the retriever queries fail."""
    pass
