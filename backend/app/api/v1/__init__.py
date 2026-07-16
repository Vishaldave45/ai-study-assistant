from fastapi import APIRouter

from .auth_routes import router as auth_router
from .workspace_routes import router as workspace_router
from .document_routes import router as document_router
from .llm_routes import router as llm_router
from .rag_routes import router as rag_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(workspace_router)
api_router.include_router(document_router)
api_router.include_router(llm_router)
api_router.include_router(rag_router)
