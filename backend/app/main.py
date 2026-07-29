import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.exceptions.auth import AuthError
from app.exceptions.document import DocumentError
from app.exceptions.workspace import WorkspaceError
from app.llm.exceptions import LLMRateLimit
from app.rag.exceptions import RAGException

logger = logging.getLogger(__name__)

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
)

# 1. Enable CORS Middleware for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Global Domain & Unhandled Exception Handlers (Security & Hygiene)
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
        content={"detail": str(exc)},
    )


@app.exception_handler(DocumentError)
async def document_error_handler(request: Request, exc: DocumentError):
    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
        content={"detail": str(exc)},
    )


@app.exception_handler(WorkspaceError)
async def workspace_error_handler(request: Request, exc: WorkspaceError):
    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
        content={"detail": str(exc)},
    )


@app.exception_handler(LLMRateLimit)
async def llm_rate_limit_handler(request: Request, exc: LLMRateLimit):
    logger.warning(f"Gemini Rate Limit Exceeded on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Gemini rate limit exceeded (20 RPM free tier quota). Please wait a few seconds before retrying."},
    )


@app.exception_handler(RAGException)
async def rag_exception_handler(request: Request, exc: RAGException):
    logger.warning(f"RAG Exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Server Error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


# 3. Include API Router
app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def health():
    return {"status": "ok"}
