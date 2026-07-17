from uuid import UUID
from pydantic import BaseModel


class SearchRequest(BaseModel):
    workspace_id: UUID
    query: str


class SearchResponseItem(BaseModel):
    chunk_id: UUID
    document_id: UUID
    score: float
    content: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResponseItem]
