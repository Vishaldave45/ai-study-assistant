from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class WorkspaceResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
