from app.schemas.base import BaseSchema


class DocumentChunkSchema(BaseSchema):
    index: int
    content: str
    character_count: int
    token_count: int
    start_offset: int
    end_offset: int
