from app.llm.gemini import GeminiProvider
from app.llm.provider import LLMProvider


class LLMFactory:

    @staticmethod
    def create(provider_type: str = "gemini") -> LLMProvider:
        """
        Instantiate and return the requested LLM provider.
        """
        p_type = provider_type.lower()
        if p_type == "gemini":
            return GeminiProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")
