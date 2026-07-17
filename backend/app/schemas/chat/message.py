from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.database.enums import MessageRole
from app.schemas.base import BaseSchema
from app.schemas.chat.common import BasePagination


class CitationResponse(BaseSchema):
    """
    Schema for document chunk citations.
    """
    document_id: UUID = Field(..., description="ID of the cited document")
    document_name: str = Field(..., description="Original filename of the cited document")
    page: str = Field(..., description="Page number or identifier in the document")
    score: float = Field(..., description="Relevance score of the citation")


class MessageResponse(BaseSchema):
    """
    Response schema representing a single message.
    """
    id: UUID
    role: MessageRole = Field(..., description="The role of the message sender (USER, ASSISTANT, etc.)")
    content: str = Field(..., description="Content of the message")
    created_at: datetime
    citations: list[CitationResponse] = Field(default_factory=list, description="Citations used in the message")


class MessageListResponse(BasePagination):
    """
    Paginated response schema for a list of messages.
    """
    messages: list[MessageResponse] = Field(..., description="List of messages in the page")
