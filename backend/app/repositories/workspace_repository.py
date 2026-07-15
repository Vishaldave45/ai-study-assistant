from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.database.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):

    def get_by_id(self,workspace_id: UUID,) -> Workspace | None:
        return super().get_by_id(Workspace, workspace_id)

    def list_by_owner(self,owner_id: UUID,) -> list[Workspace]:
       statement = (select(Workspace).where(Workspace.owner_id == owner_id).order_by(Workspace.created_at.asc()))
       result = self.db.execute(statement)
       return list(result.scalars().all())

    def get_by_owner_and_name(self,owner_id: UUID,name: str,) -> Workspace | None:
        statement = (select(Workspace).where(Workspace.owner_id == owner_id,Workspace.name == name,))

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def exists_for_owner(self,owner_id: UUID,name: str,) -> bool:
       return (
            self.get_by_owner_and_name(owner_id, name)
            is not None
        )