import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.models.user import User
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

from app.dependencies.chat import get_conversation_service
from app.exceptions.chat import (
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationNotFoundError,
)
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceNotFoundError,
)
from app.schemas.chat import (
    ConversationListResponse,
    ConversationResponse,
    CreateConversationRequest,
    RenameConversationRequest,
    SuccessResponse,
)
from app.services.chat.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Creates a new conversation with the default title inside the specified workspace.",
)
def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    try:
        conversation = service.create_conversation(
            workspace_id=request.workspace_id,
            user_id=current_user.id,
        )
        return ConversationResponse.model_validate(conversation)
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List conversations",
    description="Retrieves a paginated list of active conversations in a workspace, sorted by last_message_at DESC.",
)
def list_conversations(
    workspace_id: UUID = Query(..., description="The workspace ID to list conversations for"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationListResponse:
    try:
        conversations, total, total_pages = service.list_conversations(
            workspace_id=workspace_id,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
        )
        # Note: SQLAlchemy models will map last_message_preview later, default to None or blank for summaries
        items = []
        for c in conversations:
            # Generate preview: last message content or None
            # (In the future, we will populate this from the messages relation)
            preview = None
            if c.messages:
                # Sort messages by created_at desc to get last message
                sorted_msgs = sorted(c.messages, key=lambda m: m.created_at, reverse=True)
                preview = sorted_msgs[0].content[:100] if sorted_msgs else None

            items.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "last_message_preview": preview,
                    "last_message_at": c.last_message_at,
                }
            )

        return ConversationListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation metadata",
    description="Retrieves metadata for a specific conversation.",
)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    try:
        conversation = service.get_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        return ConversationResponse.model_validate(conversation)
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Rename conversation",
    description="Renames an active conversation.",
)
def rename_conversation(
    conversation_id: UUID,
    request: RenameConversationRequest,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    try:
        conversation = service.rename_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            new_title=request.title,
        )
        return ConversationResponse.model_validate(conversation)
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{conversation_id}/archive",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive conversation",
    description="Archives a conversation so that it can no longer receive messages.",
)
def archive_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    try:
        conversation = service.archive_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        return ConversationResponse.model_validate(conversation)
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{conversation_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete conversation",
    description="Soft-deletes a conversation.",
)
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> SuccessResponse:
    try:
        service.delete_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        return SuccessResponse(message="Conversation deleted successfully.")
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ----------------------------------------------------
# Chat Router for RAG messages
# ----------------------------------------------------
from app.dependencies.chat import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat.chat_service import ChatService

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI",
    description="Sends a query inside a conversation, retrieves context from indexed documents, and invokes the LLM to get a grounded answer with citations.",
)
def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        return service.chat(
            conversation_id=request.conversation_id,
            question=request.question,
            current_user=current_user,
        )
    except (WorkspaceNotFoundError, ConversationNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (WorkspaceAccessDeniedError, ConversationAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ConversationArchivedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception(f"Unhandled error in send_message endpoint: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response",
        ) from exc

