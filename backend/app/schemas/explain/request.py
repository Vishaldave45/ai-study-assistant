from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema
from app.prompts.explain.templates import ExplainLevel


class ExplainRequest(BaseSchema):
    workspace_id: UUID = Field(
        ...,
        description="The ID of the workspace containing the document chunks."
    )
    concept: str = Field(
        ...,
        min_length=1,
        description="The concept or term to be explained."
    )
    level: ExplainLevel = Field(
        ExplainLevel.BEGINNER,
        description="Target depth/mode for the explanation (beginner, intermediate, advanced, interview, analogy)."
    )
    document_id: UUID | None = Field(
        None,
        description="Optional ID of a specific document to retrieve chunks from. If not provided, semantic search will run workspace-wide."
    )
