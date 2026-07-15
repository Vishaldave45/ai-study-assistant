from app.schemas.base import BaseSchema


class ProcessedText(BaseSchema):
    text: str
    character_count: int
    line_count: int
    word_count: int
