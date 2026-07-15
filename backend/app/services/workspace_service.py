import logging
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

logger = logging.getLogger(__name__)


class WorkspaceService:

    def __init__(self, db: Session):
        self.db = db
        self.workspaces = WorkspaceRepository(db)

    def _validate_owner(
        self,
        workspace: Workspace,
        owner_id: UUID,
        action: str = "access",
    ) -> None:
        if workspace.owner_id != owner_id:
            logger.warning(
                f"Unauthorized workspace {action} attempt on "
                f"workspace {workspace.id} by user {owner_id}"
            )
            raise WorkspaceAccessDeniedError(
                f"Only the owner can {action} this workspace."
            )

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
            logger.info(
                f"Workspace Created: {workspace.id} by user {owner_id}"
            )
        except Exception:
            self.db.rollback()
            raise

        return workspace

    def list_workspaces(
        self,
        owner_id: UUID,
        page: int = 1,
        page_size: int = 10,
        query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "asc",
    ) -> tuple[list[Workspace], int, int]:
        skip = (page - 1) * page_size
        limit = page_size

        total = self.workspaces.count(owner_id=owner_id, query=query)
        workspaces = self.workspaces.paginate(
            owner_id=owner_id,
            skip=skip,
            limit=limit,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return workspaces, total, total_pages

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

        self._validate_owner(workspace, owner_id, action="access")

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

        self._validate_owner(workspace, owner_id, action="update")

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
            logger.info(
                f"Workspace Updated: {workspace.id} by user {owner_id}"
            )
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

        self._validate_owner(workspace, owner_id, action="delete")

        self.workspaces.delete(workspace)

        try:
            self.db.commit()
            logger.info(
                f"Workspace Deleted: {workspace_id} by user {owner_id}"
            )
        except Exception:
            self.db.rollback()
            raise
