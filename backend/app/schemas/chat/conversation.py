from datetime import datetime
from uuid import UUID
from typing import Annotated

from pydantic import Field, field_validator

from app.database.enums import ConversationStatus
from app.schemas.base import BaseSchema
from app.schemas.chat.common import BasePagination


class CreateConversationRequest(BaseSchema):
    """
    Schema for creating a new conversation.
    """
    workspace_id: UUID = Field(..., description="The workspace ID where the conversation will be created")


class RenameConversationRequest(BaseSchema):
    """
    Schema for renaming an existing conversation.
    """
    title: Annotated[str, Field(max_length=255, description="The new title of the conversation")]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v:
            raise ValueError("Title cannot be empty")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty or contain only whitespace")
        if len(trimmed) > 255:
            raise ValueError("Title cannot exceed 255 characters")
        return trimmed


class ConversationResponse(BaseSchema):
    """
    Detailed response schema for a conversation.
    """
    id: UUID
    workspace_id: UUID
    title: str
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


class ConversationSummaryResponse(BaseSchema):
    """
    Summary response schema for sidebar listing.
    """
    id: UUID
    title: str
    last_message_preview: str | None = Field(None, description="A preview of the last message in the conversation")
    last_message_at: datetime = Field(..., description="Timestamp of the last message sent in this conversation")


class ConversationListResponse(BasePagination):
    """
    Paginated list response for conversations.
    """
    items: list[ConversationSummaryResponse] = Field(..., description="List of conversation summaries")
