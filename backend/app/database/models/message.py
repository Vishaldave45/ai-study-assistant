from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import MessageRole
from app.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.database.models.conversation import Conversation
    from app.database.models.message_citation import MessageCitation


class Message(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "messages"

    conversation_id = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole, native_enum=False),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    citations: Mapped[list["MessageCitation"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Message(id={self.id}, "
            f"conversation_id={self.conversation_id}, "
            f"role='{self.role}')"
        )
