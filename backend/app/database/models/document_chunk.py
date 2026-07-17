from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.document import Document


class DocumentChunk(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "document_chunks"

    document_id = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    start_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    end_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks",
    )

    def __repr__(self) -> str:
        return (
            f"DocumentChunk(id={self.id}, "
            f"document_id={self.document_id}, "
            f"chunk_index={self.chunk_index}, "
            f"token_count={self.token_count})"
        )
