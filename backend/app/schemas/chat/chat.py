from uuid import UUID
from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema
from app.schemas.chat.common import TokenUsage
from app.schemas.chat.message import CitationResponse


class ChatRequest(BaseSchema):
    """
    Request schema for sending a user message to a chat conversation.
    """
    conversation_id: UUID = Field(..., description="ID of the conversation to send the message to")
    question: Annotated[str, Field(min_length=1, max_length=5000, description="The user's question or prompt")]

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        if not v:
            raise ValueError("Question cannot be empty")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or contain only whitespace")
        if len(trimmed) > 5000:
            raise ValueError("Question cannot exceed 5000 characters")
        return trimmed


class TokenUsageResponse(TokenUsage):
    """
    Response schema for token usage tracking.
    """
    pass


class ChatResponse(BaseSchema):
    """
    Response schema for a chat reply.
    """
    conversation_id: UUID = Field(..., description="ID of the conversation")
    message_id: UUID = Field(..., description="ID of the newly created assistant message")
    answer: str = Field(..., description="The assistant's response to the question")
    citations: list[CitationResponse] = Field(..., description="Citations and references used in the response")
    usage: TokenUsageResponse = Field(..., description="Token usage details for the AI generation")
