from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from app.database.models.user import User


class RefreshToken(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "refresh_tokens"

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id}, " f"user_id={self.user_id})"
