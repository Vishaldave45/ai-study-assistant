import logging
import tiktoken

logger = logging.getLogger(__name__)


class TokenBudgetManager:

    def __init__(self, max_tokens: int = 6000, model_name: str = "gpt-4"):
        self.max_tokens = max_tokens
        self.model_name = model_name
        try:
            try:
                self.encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                # Fall back to default cl100k_base encoding used by newer models
                self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(
                f"Could not initialize tiktoken encoding: {e}. Using fallback character approximation."
            )
            self.encoding = None

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the given text string.
        """
        if not text:
            return 0
        if self.encoding is not None:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.debug(f"Tiktoken encoding failed: {e}")
        # Fallback: hybrid word count & character length approximation
        words = len(text.split())
        chars_approx = int(len(text) / 5.0)
        return max(1, words, chars_approx)

    def trim_context(
        self, system_prompt: str, question: str, chunks_formatted: list[str]
    ) -> list[str]:
        """
        Trims the context chunks list to ensure the total prompt fits within the max_tokens limit.
        """
        base_prompt = (
            "=====================================\n"
            "System Instruction\n"
            "=====================================\n"
            f"{system_prompt}\n\n"
            "=====================================\n"
            "Context\n"
            "=====================================\n\n\n"
            "=====================================\n"
            "Question\n"
            "=====================================\n"
            f"{question}\n\n"
            "=====================================\n"
            "Assistant"
        )
        base_tokens = self.count_tokens(base_prompt)

        # Calculate how many tokens we can allocate for chunks
        allowed_tokens = self.max_tokens - base_tokens

        if allowed_tokens <= 0:
            logger.error("Base prompt size exceeds the total allowed token budget!")
            return []

        current_tokens = 0
        accepted_chunks = []

        for chunk in chunks_formatted:
            # We add a newline separator between chunks in the prompt
            chunk_tokens = self.count_tokens(chunk + "\n---\n")
            if current_tokens + chunk_tokens <= allowed_tokens:
                accepted_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                logger.warning(
                    f"Token budget of {self.max_tokens} reached. "
                    f"Trimming remaining {len(chunks_formatted) - len(accepted_chunks)} chunks."
                )
                break

        return accepted_chunks
