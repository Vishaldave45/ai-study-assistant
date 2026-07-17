from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database.base import Base
from app.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.database.models.message import Message
    from app.database.models.document_chunk import DocumentChunk


class MessageCitation(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "message_citations"

    message_id = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_chunk_id = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    message: Mapped["Message"] = relationship(back_populates="citations")
    document_chunk: Mapped["DocumentChunk"] = relationship()

    @property
    def document_id(self) -> UUID:
        return self.document_chunk.document_id

    @property
    def document_name(self) -> str:
        return self.document_chunk.document.original_filename

    @property
    def page(self) -> str:
        return "N/A"

    @property
    def score(self) -> float:
        return 0.0

    def __repr__(self) -> str:
        return (
            f"MessageCitation(id={self.id}, "
            f"message_id={self.message_id}, "
            f"document_chunk_id={self.document_chunk_id})"
        )
