
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.database.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def get_by_id(self,user_id: UUID,) -> User | None:
        statement = (
        select(User)
        .where(User.id == user_id)
    )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_by_email(self,email: str,) -> User | None:
        statement = (select(User).where(User.email == email))

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def exists_by_email(self,email: str,) -> bool:
        return self.get_by_email(email) is not None