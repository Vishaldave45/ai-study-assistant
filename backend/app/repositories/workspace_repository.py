from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.database.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):

    def create(
        self,
        owner_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Workspace:
        workspace = Workspace(
            owner_id=owner_id,
            name=name,
            description=description,
        )
        self.add(workspace)
        self.flush()
        return workspace

    def get_by_id(
        self,
        workspace_id: UUID,
    ) -> Workspace | None:
        statement = (
            select(Workspace)
            .where(
                Workspace.id == workspace_id,
                Workspace.deleted_at.is_(None),
            )
        )
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def list_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Workspace]:
        statement = (
            select(Workspace)
            .where(
                Workspace.owner_id == owner_id,
                Workspace.deleted_at.is_(None),
            )
            .order_by(Workspace.created_at.asc())
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def get_by_owner_and_name(
        self,
        owner_id: UUID,
        name: str,
    ) -> Workspace | None:
        statement = (
            select(Workspace)
            .where(
                Workspace.owner_id == owner_id,
                Workspace.name == name,
                Workspace.deleted_at.is_(None),
            )
        )
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def exists_by_name(
        self,
        owner_id: UUID,
        name: str,
    ) -> bool:
        return self.get_by_owner_and_name(owner_id, name) is not None

    def update(
        self,
        workspace: Workspace,
        **kwargs,
    ) -> Workspace:
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        self.flush()
        return workspace

    def delete(
        self,
        workspace: Workspace,
    ) -> None:
        workspace.deleted_at = datetime.now(UTC)
        self.flush()

    def search(
        self,
        owner_id: UUID,
        query: str,
    ) -> list[Workspace]:
        statement = (
            select(Workspace)
            .where(
                Workspace.owner_id == owner_id,
                Workspace.deleted_at.is_(None),
                (
                    Workspace.name.ilike(f"%{query}%")
                    | Workspace.description.ilike(f"%{query}%")
                ),
            )
            .order_by(Workspace.created_at.asc())
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def paginate(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Workspace]:
        statement = (
            select(Workspace)
            .where(
                Workspace.owner_id == owner_id,
                Workspace.deleted_at.is_(None),
            )
            .order_by(Workspace.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def count(
        self,
        owner_id: UUID,
    ) -> int:
        statement = (
            select(func.count(Workspace.id))
            .where(
                Workspace.owner_id == owner_id,
                Workspace.deleted_at.is_(None),
            )
        )
        return self.db.execute(statement).scalar() or 0