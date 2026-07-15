class DocumentError(Exception):
    """Base exception for all document-related errors."""
    pass


class DocumentNotFoundError(DocumentError):
    """Raised when a document is not found."""
    pass


class DocumentAccessDeniedError(DocumentError):
    """Raised when access to a document is denied."""
    pass


class InvalidFileTypeError(DocumentError):
    """Raised when the uploaded file type is invalid."""
    pass


class FileSizeExceededError(DocumentError):
    """Raised when the uploaded file size exceeds the limit."""
    pass
