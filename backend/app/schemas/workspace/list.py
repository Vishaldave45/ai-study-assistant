from app.schemas.base import BaseSchema
from .response import WorkspaceSummaryResponse


class WorkspaceListResponse(BaseSchema):
    items: list[WorkspaceSummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
