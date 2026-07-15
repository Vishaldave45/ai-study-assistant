from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from app.database.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        statement = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_active_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def list_active_by_user(
        self,
        user_id,
    ) -> list[RefreshToken]:

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def revoke(
        self,
        token: RefreshToken,
    ) -> None:

        token.revoked_at = datetime.now(UTC)

    def revoke_all_by_user(
        self,
        user_id,
    ) -> None:

        tokens = self.list_active_by_user(user_id)

        for token in tokens:
            token.revoked_at = datetime.now(UTC)

    def update_last_used(
        self,
        token: RefreshToken,
    ) -> None:

        token.last_used_at = datetime.now(UTC)

    def delete_expired(
        self,
        current_time: datetime,
    ) -> int:

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.expires_at < current_time
            )
        )

        tokens = self.db.execute(statement).scalars().all()

        for token in tokens:
            self.db.delete(token)

        return len(tokens)