from fastapi import APIRouter, Depends, HTTPException, status
from app.llm.schemas import LLMRequest, LLMResponse
from app.llm.service import LLMService
from app.llm.exceptions import LLMError, LLMRateLimit, LLMTimeout
from app.dependencies.auth import get_current_user
from app.database.models.user import User

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post(
    "/test",
    response_model=LLMResponse,
    status_code=status.HTTP_200_OK,
    summary="Test LLM Provider generation",
    description="Sends a direct prompt request to the LLM and returns the structured response.",
)
def test_llm(
    request: LLMRequest,
    current_user: User = Depends(get_current_user),
) -> LLMResponse:
    # Use gemini provider by default
    try:
        service = LLMService(provider_type="gemini")
        response = service.generate(request.prompt)
        return response
    except LLMTimeout as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except LLMRateLimit as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc
