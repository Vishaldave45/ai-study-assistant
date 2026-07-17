from pydantic import Field

from app.schemas.base import BaseSchema


class WorkspaceUpdateRequest(BaseSchema):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="The updated name of the workspace.",
    )

    description: str | None = Field(
        None, max_length=1000, description="The updated description of the workspace."
    )
