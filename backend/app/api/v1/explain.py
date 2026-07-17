import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.database.models.user import User
from app.schemas.explain.request import ExplainRequest
from app.schemas.explain.response import ExplainResponse
from app.services.explain.service import ExplainService
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError

router = APIRouter(prefix="/explain", tags=["Explain"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain a concept from workspace document chunks",
    description="Validates access, performs semantic search to retrieve context chunks, "
                "compiles a targeted concept explanation prompt (beginner, intermediate, advanced, interview, or analogy), "
                "calls Gemini, and parses the structured JSON response.",
)
def explain_concept(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExplainResponse:
    """
    Explain study concepts at varying depths (beginner, intermediate, advanced, interview, analogy) 
    using indexed workspace document chunks.
    """
    try:
        service = ExplainService(db)
        return service.explain_concept(
            workspace_id=request.workspace_id,
            current_user_id=current_user.id,
            request=request,
        )
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
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error(f"Unexpected error in explain_concept: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc
