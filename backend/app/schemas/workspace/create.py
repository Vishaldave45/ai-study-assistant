from pydantic import Field

from app.schemas.base import BaseSchema


class WorkspaceCreateRequest(BaseSchema):
    name: str = Field(
        ..., min_length=1, max_length=255, description="The name of the workspace."
    )

    description: str | None = Field(
        None, max_length=1000, description="An optional description of the workspace."
    )
