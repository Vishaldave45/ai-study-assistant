from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceUpdateRequest,
    MessageResponse,
)
from app.services.workspace.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    request: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceDetailResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.create_workspace(
            owner_id=current_user.id,
            request=request,
        )
        return WorkspaceDetailResponse.model_validate(workspace)
    except WorkspaceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=WorkspaceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_workspaces(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    query: str | None = Query(None, description="Search query"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceListResponse:
    # Validate sort_by field to avoid SQL injection / invalid fields
    allowed_sort_fields = {"name", "created_at", "updated_at"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sorting by '{sort_by}' is not supported. Allowed fields: {', '.join(allowed_sort_fields)}",
        )

    allowed_sort_orders = {"asc", "desc"}
    if sort_order.lower() not in allowed_sort_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sort order must be 'asc' or 'desc'.",
        )

    service = WorkspaceService(db)
    workspaces, total, total_pages = service.list_workspaces(
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return WorkspaceListResponse(
        items=workspaces,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/{id}",
    response_model=WorkspaceDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceDetailResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.get_workspace(
            owner_id=current_user.id,
            workspace_id=id,
        )
        return WorkspaceDetailResponse.model_validate(workspace)
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
    response_model=WorkspaceDetailResponse,
    status_code=status.HTTP_200_OK,
)
def update_workspace(
    id: UUID,
    request: WorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceDetailResponse:
    service = WorkspaceService(db)
    try:
        workspace = service.update_workspace(
            owner_id=current_user.id,
            workspace_id=id,
            request=request,
        )
        return WorkspaceDetailResponse.model_validate(workspace)
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
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = WorkspaceService(db)
    try:
        service.delete_workspace(
            owner_id=current_user.id,
            workspace_id=id,
        )
        return MessageResponse(message="Workspace deleted successfully.")
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
