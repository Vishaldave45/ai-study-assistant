import logging
from app.prompts.shared.builder import PromptBuilder as SharedPromptBuilder
from app.prompts.shared.templates import RAG_SYSTEM_PROMPT
from app.prompts.shared.formatter import ContextFormatter

logger = logging.getLogger(__name__)


class PromptBuilder(SharedPromptBuilder):
    """
    PromptBuilder extended to compile context chunks, conversation history,
    and user queries within a token budget limit.
    """

    def build_with_history(
        self,
        query: str,
        chunks: list[dict],
        history: list,
    ) -> tuple[str, int]:
        """
        Builds the final RAG prompt incorporating conversation memory.
        
        - query: The current question content.
        - chunks: List of dicts, each containing 'content', 'filename', and optionally 'page'.
        - history: Chronological list of message ORM objects or dicts (each having 'role' and 'content').
        
        Returns:
            A tuple of (compiled prompt string, number of chunks actually used).
        """
        # 1. Format each chunk
        formatted_chunks = []
        for chunk in chunks[: self.max_chunks]:
            formatted = ContextFormatter.format_chunk(
                content=chunk["content"],
                filename=chunk["filename"],
                page=chunk.get("page", "N/A"),
            )
            formatted_chunks.append(formatted)

        # 2. Format conversation history
        history_lines = []
        for msg in history:
            role = getattr(msg, "role", "")
            # Handle if role is an Enum or string
            role_str = getattr(role, "value", str(role)).upper()
            
            if role_str == "USER":
                history_lines.append(f"User: {msg.content}")
            elif role_str == "ASSISTANT":
                history_lines.append(f"Assistant: {msg.content}")
            else:
                history_lines.append(f"{role_str.capitalize()}: {msg.content}")

        history_str = "\n".join(history_lines)

        # 3. Trim context chunks using budget manager
        # Construct the base prompt prefix with history to allocate budget correctly
        combined_instruction = (
            f"{RAG_SYSTEM_PROMPT}\n\n"
            "=====================================\n"
            "Conversation History\n"
            "=====================================\n"
            f"{history_str}"
        )

        trimmed_chunks = self.budget_manager.trim_context(
            system_prompt=combined_instruction,
            question=query,
            chunks_formatted=formatted_chunks,
        )

        # 4. Assemble the final prompt
        context_str = "\n---\n".join(trimmed_chunks)

        prompt = (
            "=====================================\n"
            "System Instruction\n"
            "=====================================\n"
            f"{RAG_SYSTEM_PROMPT}\n\n"
            "=====================================\n"
            "Conversation History\n"
            "=====================================\n"
            f"{history_str}\n\n"
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

        return prompt, len(trimmed_chunks)
