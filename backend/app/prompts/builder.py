import logging
from app.prompts.config import MAX_CONTEXT_CHUNKS, MAX_PROMPT_TOKENS
from app.prompts.templates import RAG_SYSTEM_PROMPT
from app.prompts.formatter import ContextFormatter
from app.prompts.budget import TokenBudgetManager
from app.prompts.exceptions import PromptTooLargeError

logger = logging.getLogger(__name__)


class PromptBuilder:

    def __init__(
        self,
        max_tokens: int = MAX_PROMPT_TOKENS,
        max_chunks: int = MAX_CONTEXT_CHUNKS,
    ):
        self.max_chunks = max_chunks
        self.budget_manager = TokenBudgetManager(max_tokens=max_tokens)

    def build(self, query: str, chunks: list[dict]) -> str:
        """
        Builds the final formatted RAG prompt.
        Each dict inside chunks must contain:
        - content: str
        - filename: str
        - page: str (optional)
        """
        # 1. Format each chunk
        formatted_chunks = []
        for chunk in chunks[:self.max_chunks]:
            formatted = ContextFormatter.format_chunk(
                content=chunk["content"],
                filename=chunk["filename"],
                page=chunk.get("page", "N/A"),
            )
            formatted_chunks.append(formatted)

        # 2. Trim context chunks if they exceed the token budget
        trimmed_chunks = self.budget_manager.trim_context(
            system_prompt=RAG_SYSTEM_PROMPT,
            question=query,
            chunks_formatted=formatted_chunks,
        )

        # If we had chunks, but none were accepted, check if the base query is already too large
        if not trimmed_chunks and formatted_chunks:
            base_prompt = (
                "=====================================\n"
                "System Instruction\n"
                "=====================================\n"
                f"{RAG_SYSTEM_PROMPT}\n\n"
                "=====================================\n"
                "Context\n"
                "=====================================\n\n\n"
                "=====================================\n"
                "Question\n"
                "=====================================\n"
                f"{query}\n\n"
                "=====================================\n"
                "Assistant"
            )
            if self.budget_manager.count_tokens(base_prompt) > self.budget_manager.max_tokens:
                raise PromptTooLargeError(
                    f"The query is too large to fit in the token budget of {self.budget_manager.max_tokens}."
                )

        # 3. Assemble components into the final prompt structure
        context_str = "\n---\n".join(trimmed_chunks)

        prompt = (
            "=====================================\n"
            "System Instruction\n"
            "=====================================\n"
            f"{RAG_SYSTEM_PROMPT}\n\n"
            "=====================================\n"
            "Context\n"
            "=====================================\n"
            f"{context_str}\n\n"
            "=====================================\n"
            "Question\n"
            "=====================================\n"
            f"{query}\n\n"
            "=====================================\n"
            "Assistant"
        )
        return prompt
