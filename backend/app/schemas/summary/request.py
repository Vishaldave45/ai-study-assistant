from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema
from app.prompts.summary.templates import SummaryTemplateType


class SummaryRequest(BaseSchema):
    workspace_id: UUID = Field(
        ...,
        description="The ID of the workspace containing the document chunks."
    )
    document_id: UUID | None = Field(
        None,
        description="Optional ID of a specific document to summarize. If not provided, chunks from all documents in the workspace will be used."
    )
    template_type: SummaryTemplateType = Field(
        SummaryTemplateType.SHORT,
        description="The format/type of summary to generate (e.g., short, detailed, bullet, revision_notes, key_takeaways)."
    )
