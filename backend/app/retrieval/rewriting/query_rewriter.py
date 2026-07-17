import logging
from app.llm.service import LLMService

logger = logging.getLogger(__name__)


class QueryRewriter:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def rewrite(self, query: str, history: list) -> str:
        """
        Rewrites a search query based on conversation history.
        """
        if not history:
            return query

        history_lines = []
        for msg in history:
            role = getattr(msg, "role", "")
            role_str = getattr(role, "value", str(role)).upper()
            content = getattr(msg, "content", "")
            if not content and isinstance(msg, dict):
                content = msg.get("content", "")
                role_str = msg.get("role", "").upper()

            if role_str == "USER":
                history_lines.append(f"User: {content}")
            elif role_str == "ASSISTANT":
                history_lines.append(f"Assistant: {content}")

        history_str = "\n".join(history_lines)
        if not history_str.strip():
            return query

        prompt = (
            "You are an expert search query refiner. Given the conversation history and a follow-up question, "
            "rewrite the follow-up question into a single, self-contained search-optimized query.\n"
            "Do NOT add any quotes, markdown formatting, or explanations. Just return the raw rewritten query.\n\n"
            "Conversation History:\n"
            f"{history_str}\n\n"
            f"Follow-up Question: {query}\n"
            "Rewritten Query:"
        )

        try:
            response = self.llm_service.generate(prompt)
            rewritten = response.answer.strip()
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1].strip()
            return rewritten if rewritten else query
        except Exception as e:
            logger.error(f"Failed to rewrite query: {e}")
            return query
