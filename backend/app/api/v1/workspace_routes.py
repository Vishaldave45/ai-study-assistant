from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
)
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    request: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.create_workspace(
            owner_id=current_user.id,
            request=request,
        )
        return WorkspaceResponse.model_validate(workspace)
    except WorkspaceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[WorkspaceResponse],
    status_code=status.HTTP_200_OK,
)
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkspaceResponse]:
    service = WorkspaceService(db)
    workspaces = service.list_workspaces(owner_id=current_user.id)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.get(
    "/{id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
)
def get_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.get_workspace(
            owner_id=current_user.id,
            workspace_id=id,
        )
        return WorkspaceResponse.model_validate(workspace)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
)
def update_workspace(
    id: UUID,
    request: WorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.update_workspace(
            owner_id=current_user.id,
            workspace_id=id,
            request=request,
        )
        return WorkspaceResponse.model_validate(workspace)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
)
def delete_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkspaceService(db)
    try:
        service.delete_workspace(
            owner_id=current_user.id,
            workspace_id=id,
        )
        return {"message": "Workspace deleted successfully."}
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
