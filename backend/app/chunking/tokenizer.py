import logging

logger = logging.getLogger(__name__)

try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("cl100k_base")
except Exception as e:
    logger.warning(
        f"Could not initialize tiktoken cl100k_base. Using fallback character approximation: {e}"
    )
    _ENCODING = None


class TokenCounter:

    @classmethod
    def count_tokens(cls, text: str) -> int:
        if not text:
            return 0
        if _ENCODING is not None:
            try:
                return len(_ENCODING.encode(text))
            except Exception as e:
                logger.debug(f"Tiktoken encoding failed: {e}")

        # Fallback: Approx 4 characters per token
        return max(1, len(text) // 4)
