from abc import ABC, abstractmethod
from typing import Generator
from app.llm.schemas import LLMResponse


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """
        Send prompt to LLM and return a structured response.
        """
        pass

    @abstractmethod
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Send prompt to LLM and yield chunk strings.
        """
        pass

    @abstractmethod
    def model_name(self) -> str:
        """
        Returns the configured model name.
        """
        pass
