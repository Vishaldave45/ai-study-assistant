from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.database.models.conversation import Conversation
    from app.database.models.document import Document


class ConversationDocument(
    TimestampMixin,
    Base,
):
    __tablename__ = "conversation_documents"

    conversation_id = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    document_id = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="documents")
    document: Mapped["Document"] = relationship(back_populates="conversations")

    def __repr__(self) -> str:
        return (
            f"ConversationDocument(conversation_id={self.conversation_id}, "
            f"document_id={self.document_id})"
        )
