from fastapi import APIRouter

from .auth_routes import router as auth_router
from .workspace_routes import router as workspace_router
from .document_routes import router as document_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(workspace_router)
api_router.include_router(document_router)