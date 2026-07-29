import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.database.models.user import User
from app.rag.schemas import QuestionRequest, AnswerResponse
from app.rag.service import RAGService
from app.rag.exceptions import WorkspaceNotFound, RAGException, GenerationFailed
from app.llm.exceptions import LLMRateLimit

router = APIRouter(prefix="/rag", tags=["RAG"])
logger = logging.getLogger(__name__)


@router.post(
    "/query",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Query workspace documents",
    description="Searches indexed chunks in a workspace and returns an LLM-generated answer with citations.",
)
def query_workspace(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnswerResponse:
    try:
        service = RAGService(db)
        return service.query(request.workspace_id, request.question, current_user.id)
    except WorkspaceNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except LLMRateLimit as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini rate limit exceeded (20 RPM free tier limit). Please retry in a few seconds.",
        ) from exc
    except RAGException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except GenerationFailed as exc:
        err_str = str(exc).lower()
        if "rate limit" in err_str or "429" in err_str or "quota" in err_str:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini rate limit exceeded (20 RPM free tier limit). Please retry in a few seconds.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        err_str = str(exc).lower()
        if "rate limit" in err_str or "429" in err_str or "quota" in err_str:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini rate limit exceeded (20 RPM free tier limit). Please retry in a few seconds.",
            ) from exc
        logger.error(f"Unexpected error in /rag/query: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="RAG health check",
    description="Returns connectivity and initialization status of RAG dependencies.",
)
def rag_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        from app.embedding.service import EmbeddingService
        embedding_status = "loaded"
    except Exception:
        embedding_status = "error"

    try:
        from app.vectorstore.faiss_store import FAISSVectorStore
        store = FAISSVectorStore()
        vector_status = "loaded"
    except Exception:
        vector_status = "error"

    try:
        from app.llm.service import LLMService
        llm_status = "connected"
    except Exception:
        llm_status = "disconnected"

    overall = (
        "healthy"
        if "error" not in [embedding_status, vector_status]
        and llm_status == "connected"
        else "unhealthy"
    )

    return {
        "status": overall,
        "embedding": embedding_status,
        "vector_store": vector_status,
        "llm": llm_status,
    }
