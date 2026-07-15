from app.schemas.base import BaseSchema


class ParsedPDF(BaseSchema):
    title: str | None
    author: str | None
    subject: str | None
    creator: str | None
    producer: str | None
    keywords: str | None
    page_count: int
    text: str
    metadata: dict
