from typing import Generator, List, Union
from app.llm.provider import LLMProvider
from app.llm.schemas import LLMResponse


class FakeProvider(LLMProvider):
    """
    Test double implementation of LLMProvider interface.
    Records all prompt calls and returns queued responses or raises queued exceptions.
    """

    def __init__(self, default_text: str = "Fake LLM generated response"):
        self.default_text = default_text
        self.calls: List[dict] = []
        self._responses: List[Union[LLMResponse, Exception]] = []

    def queue_response(self, response: Union[LLMResponse, Exception, str]) -> None:
        """
        Queue a response or Exception to be returned/raised on subsequent calls.
        """
        if isinstance(response, str):
            response = LLMResponse(
                answer=response,
                model=self.model_name(),
                finish_reason="STOP",
                usage={"prompt_tokens": 10, "output_tokens": 10},
            )
        self._responses.append(response)

    def generate(self, prompt: str) -> LLMResponse:
        """
        Record the prompt and return queued response or default response.
        """
        self.calls.append({"method": "generate", "prompt": prompt})

        if self._responses:
            next_resp = self._responses.pop(0)
            if isinstance(next_resp, Exception):
                raise next_resp
            return next_resp

        return LLMResponse(
            answer=self.default_text,
            model=self.model_name(),
            finish_reason="STOP",
            usage={"prompt_tokens": 10, "output_tokens": 10},
        )

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Record prompt and stream chunks.
        """
        self.calls.append({"method": "stream", "prompt": prompt})

        if self._responses:
            next_resp = self._responses.pop(0)
            if isinstance(next_resp, Exception):
                raise next_resp
            yield next_resp.answer
        else:
            yield self.default_text

    def model_name(self) -> str:
        return "fake-gemini-2.5-flash"
