class PromptBuilderError(Exception):
    """Base exception for all prompt building operations."""

    pass


class PromptTooLargeError(PromptBuilderError):
    """Raised when the generated prompt is too large to fit in the token budget."""

    pass
