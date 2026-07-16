class LLMError(Exception):
    """Base exception for all LLM provider operations."""
    pass


class LLMTimeout(LLMError):
    """Raised when the LLM provider request times out."""
    pass


class LLMRateLimit(LLMError):
    """Raised when the LLM provider rate limit is exceeded."""
    pass


class InvalidModelError(LLMError):
    """Raised when an invalid model name is requested."""
    pass
