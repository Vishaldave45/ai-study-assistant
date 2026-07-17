from fastapi import APIRouter

from .auth import router as auth_router
from .workspace import router as workspace_router
from .documents import router as document_router
from .llm import router as llm_router
from .rag import router as rag_router
from .chat import router as chat_conversations_router, chat_router as message_chat_router
from .summary import router as summary_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(workspace_router)
api_router.include_router(document_router)
api_router.include_router(llm_router)
api_router.include_router(rag_router)
api_router.include_router(chat_conversations_router)
api_router.include_router(message_chat_router)
api_router.include_router(summary_router)



