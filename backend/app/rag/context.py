from uuid import UUID
from pydantic import BaseModel


class RetrievedContext(BaseModel):
    chunks: list[str]
    scores: list[float]
    document_ids: list[UUID]
    pages: list[str]
    workspace_id: UUID
