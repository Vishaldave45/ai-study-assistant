from app.llm.factory import LLMFactory
from app.llm.schemas import LLMResponse
from app.llm.exceptions import LLMError


class LLMService:

    def __init__(self, provider_type: str = "gemini"):
        self.provider = LLMFactory.create(provider_type)

    def generate(self, prompt: str) -> LLMResponse:
        """
        Validate prompt and request structured generation from the provider.
        """
        if not prompt or not prompt.strip():
            raise LLMError("Prompt cannot be empty or blank.")
        return self.provider.generate(prompt)

    def stream(self, prompt: str):
        """
        Validate prompt and request token streaming from the provider.
        """
        if not prompt or not prompt.strip():
            raise LLMError("Prompt cannot be empty or blank.")
        return self.provider.stream(prompt)
