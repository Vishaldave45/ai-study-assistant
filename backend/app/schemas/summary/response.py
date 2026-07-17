from pydantic import Field
from app.schemas.base import BaseSchema


class SummaryResponse(BaseSchema):
    summary: str = Field(
        ...,
        description="The generated summary text content."
    )
    token_usage: dict[str, int] | None = Field(
        None,
        description="Metadata on the token consumption of the prompt and generation."
    )
    chunk_count: int = Field(
        ...,
        description="The number of document chunks that were successfully compressed into the prompt context."
    )
    processing_time_ms: int = Field(
        ...,
        description="Total duration taken to retrieve chunks and generate the summary in milliseconds."
    )
    model: str = Field(
        ...,
        description="The model identifier that executed the generation (e.g. gemini-2.5-flash)."
    )
