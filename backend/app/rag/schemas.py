from uuid import UUID
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    workspace_id: UUID
    question: str = Field(..., min_length=1, description="Question content")


class CitationItem(BaseModel):
    document: str
    page: str
    score: float


class AnswerResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    chunks_used: int
    model: str
    processing_time_ms: int
