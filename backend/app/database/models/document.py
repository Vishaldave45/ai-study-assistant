from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, BigInteger, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import DocumentStatus
from app.database.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from app.database.models.workspace import Workspace
    from app.database.models.document_chunk import DocumentChunk


class Document(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    __tablename__ = "documents"

    workspace_id = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus, native_enum=False),
        nullable=False,
        default=DocumentStatus.UPLOADING,
    )

    workspace: Mapped["Workspace"] = relationship(
        back_populates="documents",
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Document(id={self.id}, "
            f"workspace_id={self.workspace_id}, "
            f"original_filename='{self.original_filename}', "
            f"status='{self.status}')"
        )
