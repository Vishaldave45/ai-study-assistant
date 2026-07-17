import logging
from app.prompts.shared.budget import TokenBudgetManager
from app.prompts.shared.exceptions import PromptTooLargeError
from app.prompts.explain.config import MAX_EXPLAIN_CHUNKS, MAX_EXPLAIN_TOKENS
from app.prompts.explain.templates import EXPLAIN_SYSTEM_PROMPT, TEMPLATES, ExplainLevel
from app.prompts.explain.formatter import ExplainFormatter

logger = logging.getLogger(__name__)


class ExplainPromptBuilder:
    """
    Constructs explain concept prompts within token budget limits, targeting specific study depth levels.
    """

    def __init__(
        self,
        max_tokens: int = MAX_EXPLAIN_TOKENS,
        max_chunks: int = MAX_EXPLAIN_CHUNKS,
    ):
        self.max_chunks = max_chunks
        self.budget_manager = TokenBudgetManager(max_tokens=max_tokens)

    def build(self, concept: str, chunks: list[dict], level: ExplainLevel) -> tuple[str, int]:
        """
        Builds the explanation generation prompt.
        Each chunk in the chunks list must contain 'content', 'filename', and optionally 'page'.
        
        Returns:
            A tuple of (compiled prompt string, number of chunks actually used).
        """
        # 1. Format the level-specific instruction template
        raw_template = TEMPLATES.get(level)
        if not raw_template:
            raise ValueError(f"Unsupported explanation level: {level}")

        instruction = raw_template.format(concept=concept)

        # 2. Format all chunks
        formatted_chunks = ExplainFormatter.format_chunks(chunks[: self.max_chunks])

        # 3. Trim context chunks using TokenBudgetManager to fit inside our budget
        trimmed_chunks = self.budget_manager.trim_context(
            system_prompt=EXPLAIN_SYSTEM_PROMPT,
            question=instruction,
            chunks_formatted=formatted_chunks,
        )

        # 4. Check if baseline instructions alone are too large
        if not trimmed_chunks and formatted_chunks:
            base_prompt = (
                "=====================================\n"
                "System Instruction\n"
                "=====================================\n"
                f"{EXPLAIN_SYSTEM_PROMPT}\n\n"
                "=====================================\n"
                "Context\n"
                "=====================================\n\n\n"
                "=====================================\n"
                "Question\n"
                "=====================================\n"
                f"{instruction}\n\n"
                "=====================================\n"
                "Assistant"
            )
            if (
                self.budget_manager.count_tokens(base_prompt)
                > self.budget_manager.max_tokens
            ):
                raise PromptTooLargeError(
                    f"Explanation instruction is too large for the token budget of {self.budget_manager.max_tokens}."
                )

        # 5. Assemble the final prompt structure
        context_str = "\n---\n".join(trimmed_chunks)

        prompt = (
            "=====================================\n"
            "System Instruction\n"
            "=====================================\n"
            f"{EXPLAIN_SYSTEM_PROMPT}\n\n"
            "=====================================\n"
            "Context\n"
            "=====================================\n"
            f"{context_str}\n\n"
            "=====================================\n"
            "Instructions\n"
            "=====================================\n"
            f"{instruction}\n\n"
            "=====================================\n"
            "JSON Response Output:"
        )

        return prompt, len(trimmed_chunks)
