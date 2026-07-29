import time
from app.llm.factory import LLMFactory
from app.llm.schemas import LLMResponse
from app.llm.exceptions import LLMError, LLMRateLimit


class LLMService:

    def __init__(self, provider_type: str = "gemini", max_retries: int = 3, retry_delay: float = 0.05):
        self.provider = LLMFactory.create(provider_type)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def generate(self, prompt: str) -> LLMResponse:
        """
        Validate prompt and request structured generation from the provider.
        Retries with exponential backoff if LLMRateLimit exception occurs.
        """
        if not prompt or not prompt.strip():
            raise LLMError("Prompt cannot be empty or blank.")

        attempts = 0
        while True:
            try:
                attempts += 1
                return self.provider.generate(prompt)
            except LLMRateLimit as e:
                if attempts >= self.max_retries:
                    raise e
                time.sleep(self.retry_delay * (2 ** (attempts - 1)))

    def stream(self, prompt: str):
        """
        Validate prompt and request token streaming from the provider.
        """
        if not prompt or not prompt.strip():
            raise LLMError("Prompt cannot be empty or blank.")
        return self.provider.stream(prompt)
