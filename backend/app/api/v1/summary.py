import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.database.models.user import User
from app.schemas.summary.request import SummaryRequest
from app.schemas.summary.response import SummaryResponse
from app.services.summary.service import SummaryService
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
from app.llm.exceptions import LLMRateLimit

router = APIRouter(prefix="/summary", tags=["Summary"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate summary from workspace document chunks",
    description="Validates access, retrieves text chunks from a specific document or the entire workspace, "
                "compiles a summary based on the requested template layout, and calls Gemini.",
)
def generate_summary(
    request: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    try:
        service = SummaryService(db)
        return service.generate_summary(
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
    except LLMRateLimit as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini rate limit exceeded (20 RPM free tier limit). Please retry in a few seconds.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        err_str = str(exc).lower()
        if "rate limit" in err_str or "429" in err_str or "quota" in err_str:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini rate limit exceeded (20 RPM free tier limit). Please retry in a few seconds.",
            ) from exc
        logger.error(f"Unexpected error in generate_summary: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc
