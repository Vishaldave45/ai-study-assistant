from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models.workspace import Workspace
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
)


class WorkspaceService:

    def __init__(self, db: Session):
        self.db = db
        self.workspaces = WorkspaceRepository(db)

    def create_workspace(
        self,
        owner_id: UUID,
        request: WorkspaceCreateRequest,
    ) -> Workspace:
        if self.workspaces.exists_by_name(owner_id, request.name):
            raise WorkspaceAlreadyExistsError(
                f"Workspace with name '{request.name}' already exists."
            )

        workspace = self.workspaces.create(
            owner_id=owner_id,
            name=request.name,
            description=request.description,
        )

        try:
            self.db.commit()
            self.db.refresh(workspace)
        except Exception:
            self.db.rollback()
            raise

        return workspace

    def list_workspaces(
        self,
        owner_id: UUID,
    ) -> list[Workspace]:
        return self.workspaces.list_by_owner(owner_id)

    def get_workspace(
        self,
        owner_id: UUID,
        workspace_id: UUID,
    ) -> Workspace:
        workspace = self.workspaces.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(
                f"Workspace with ID {workspace_id} not found."
            )

        if workspace.owner_id != owner_id:
            raise WorkspaceAccessDeniedError(
                "Access denied for this workspace."
            )

        return workspace

    def update_workspace(
        self,
        owner_id: UUID,
        workspace_id: UUID,
        request: WorkspaceUpdateRequest,
    ) -> Workspace:
        workspace = self.workspaces.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(
                f"Workspace with ID {workspace_id} not found."
            )

        if workspace.owner_id != owner_id:
            raise WorkspaceAccessDeniedError(
                "Only the owner can update this workspace."
            )

        if request.name is not None and request.name != workspace.name:
            if self.workspaces.exists_by_name(owner_id, request.name):
                raise WorkspaceAlreadyExistsError(
                    f"Workspace with name '{request.name}' already exists."
                )

        dump_data = request.model_dump(exclude_unset=True)
        self.workspaces.update(workspace, **dump_data)

        try:
            self.db.commit()
            self.db.refresh(workspace)
        except Exception:
            self.db.rollback()
            raise

        return workspace

    def delete_workspace(
        self,
        owner_id: UUID,
        workspace_id: UUID,
    ) -> None:
        workspace = self.workspaces.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(
                f"Workspace with ID {workspace_id} not found."
            )

        if workspace.owner_id != owner_id:
            raise WorkspaceAccessDeniedError(
                "Only the owner can delete this workspace."
            )

        self.workspaces.delete(workspace)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
