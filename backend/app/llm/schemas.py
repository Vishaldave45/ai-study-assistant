from pydantic import BaseModel


class LLMRequest(BaseModel):
    prompt: str


class LLMResponse(BaseModel):
    answer: str
    usage: dict | None = None
    finish_reason: str | None = None
    model: str
