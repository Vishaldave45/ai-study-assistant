from uuid import UUID
from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: UUID
    score: float
    document_id: UUID
    workspace_id: UUID


class IndexResult(BaseModel):
    chunks: int
    vectors: int
    dimension: int
