from datetime import datetime
from uuid import UUID

from app.database.enums import DocumentStatus
from app.schemas.base import BaseSchema


class DocumentResponse(BaseSchema):
    id: UUID
    workspace_id: UUID
    original_filename: str
    stored_filename: str
    mime_type: str
    file_size: int
    page_count: int | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class DocumentParsePreviewResponse(BaseSchema):
    title: str | None
    author: str | None
    page_count: int
    text_preview: str


class DocumentCleanPreviewResponse(BaseSchema):
    characters: int
    words: int
    preview: str


class DocumentChunkPreviewItem(BaseSchema):
    index: int
    preview: str


class DocumentChunkResponse(BaseSchema):
    total_chunks: int
    average_tokens: int
    chunks: list[DocumentChunkPreviewItem]


class DocumentEmbedResponse(BaseSchema):
    chunks: int
    dimension: int
    model: str
