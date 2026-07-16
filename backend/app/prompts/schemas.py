from uuid import UUID
from pydantic import BaseModel


class PromptRequest(BaseModel):
    workspace_id: UUID
    query: str


class PromptResponse(BaseModel):
    prompt: str
