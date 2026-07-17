import logging
from app.prompts.shared.budget import TokenBudgetManager
from app.prompts.shared.exceptions import PromptTooLargeError
from app.prompts.summary.config import MAX_SUMMARY_CHUNKS, MAX_SUMMARY_TOKENS
from app.prompts.summary.templates import SUMMARY_SYSTEM_PROMPT, TEMPLATES, SummaryTemplateType
from app.prompts.summary.formatter import SummaryFormatter

logger = logging.getLogger(__name__)


class SummaryPromptBuilder:
    """
    Constructs summary generation prompts within token budget limits.
    """

    def __init__(
        self,
        max_tokens: int = MAX_SUMMARY_TOKENS,
        max_chunks: int = MAX_SUMMARY_CHUNKS,
    ):
        self.max_chunks = max_chunks
        self.budget_manager = TokenBudgetManager(max_tokens=max_tokens)

    def build(self, chunks: list[dict], template_type: SummaryTemplateType) -> tuple[str, int]:
        """
        Builds the summary generation prompt.
        Each chunk in the chunks list must contain 'content', 'filename', and optionally 'page'.
        
        Returns:
            A tuple of (compiled prompt string, number of chunks actually used).
        """
        # 1. Get the prompt instruction template for the selected summary type
        instruction = TEMPLATES.get(template_type)
        if not instruction:
            raise ValueError(f"Unsupported summary template type: {template_type}")

        # 2. Format all chunks
        formatted_chunks = SummaryFormatter.format_chunks(chunks[: self.max_chunks])

        # 3. Trim context chunks using TokenBudgetManager to fit inside our budget
        trimmed_chunks = self.budget_manager.trim_context(
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            question=instruction,
            chunks_formatted=formatted_chunks,
        )

        # 4. If we have chunks, but none can fit, check if the baseline instructions alone are too large
        if not trimmed_chunks and formatted_chunks:
            base_prompt = (
                "=====================================\n"
                "System Instruction\n"
                "=====================================\n"
                f"{SUMMARY_SYSTEM_PROMPT}\n\n"
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
                    f"Summary instruction is too large for the token budget of {self.budget_manager.max_tokens}."
                )

        # 5. Assemble the final prompt structure
        context_str = "\n---\n".join(trimmed_chunks)

        prompt = (
            "=====================================\n"
            "System Instruction\n"
            "=====================================\n"
            f"{SUMMARY_SYSTEM_PROMPT}\n\n"
            "=====================================\n"
            "Context\n"
            "=====================================\n"
            f"{context_str}\n\n"
            "=====================================\n"
            "Instructions\n"
            "=====================================\n"
            f"{instruction}\n\n"
            "=====================================\n"
            "Summary Output:"
        )

        return prompt, len(trimmed_chunks)

