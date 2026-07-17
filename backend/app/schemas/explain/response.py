from pydantic import Field
from app.schemas.base import BaseSchema


class ExplainResponse(BaseSchema):
    explanation: str = Field(
        ...,
        description="The primary generated explanation text."
    )
    examples: list[str] = Field(
        default_factory=list,
        description="Illustrative examples or code snippets showcasing the concept."
    )
    important_points: list[str] = Field(
        default_factory=list,
        description="Key takeaways, highlights, or rules of thumb for this concept."
    )
    references: list[str] = Field(
        default_factory=list,
        description="Source documents and page references utilized to generate the explanation."
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Suggested self-study questions for students to self-test understanding."
    )
    processing_time_ms: int = Field(
        ...,
        description="Total duration taken to retrieve context and generate explanation in milliseconds."
    )
    model: str = Field(
        ...,
        description="The model identifier that executed the generation."
    )
