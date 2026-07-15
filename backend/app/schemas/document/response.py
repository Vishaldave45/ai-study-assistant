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
