from app.schemas.base import BaseSchema
from .response import DocumentResponse


class DocumentListResponse(BaseSchema):
    items: list[DocumentResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
