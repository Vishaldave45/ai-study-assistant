import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select

from app.database.enums import ConversationStatus
from app.database.models.conversation import Conversation
from app.exceptions.chat import (
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationNotFoundError,
)
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceNotFoundError,
)
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.workspace_repository import WorkspaceRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service layer handling all non-AI business logic for conversations.
    """

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        workspace_repo: WorkspaceRepository,
    ):
        self.conversation_repo = conversation_repo
        self.workspace_repo = workspace_repo
        self.db = conversation_repo.db

    def validate_access(self, user_id: UUID, conversation: Conversation) -> None:
        """
        Ensures the conversation belongs to the user and is associated with a workspace owned by the user.
        """
        if conversation.user_id != user_id:
            logger.warning(
                f"Access denied: User {user_id} tried to access conversation {conversation.id} owned by {conversation.user_id}"
            )
            raise ConversationAccessDeniedError("You do not have access to this conversation.")

        workspace = self.workspace_repo.get_by_id(conversation.workspace_id)
        if workspace is None:
            logger.error(f"Workspace integrity error: Workspace {conversation.workspace_id} not found for conversation {conversation.id}")
            raise WorkspaceNotFoundError(f"Workspace with ID {conversation.workspace_id} not found.")

        if workspace.owner_id != user_id:
            logger.warning(
                f"Access denied: User {user_id} tried to access conversation {conversation.id} inside workspace {workspace.id} owned by {workspace.owner_id}"
            )
            raise WorkspaceAccessDeniedError("Only the owner can access this workspace.")

    def validate_can_message(self, conversation: Conversation) -> None:
        """
        Verifies if the conversation status allows sending new messages.
        """
        if conversation.status == ConversationStatus.ARCHIVED:
            raise ConversationArchivedError("Cannot send messages to an archived conversation.")

    def generate_default_title(self) -> str:
        """
        Generates the default title for a new conversation.
        """
        return "New Chat"

    def create_conversation(
        self,
        workspace_id: UUID,
        user_id: UUID,
        title: str | None = None,
    ) -> Conversation:
        """
        Creates a new conversation in a workspace after validating user permissions.
        """
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(f"Workspace with ID {workspace_id} not found.")

        if workspace.owner_id != user_id:
            logger.warning(
                f"Unauthorized conversation creation: User {user_id} in workspace {workspace_id} owned by {workspace.owner_id}"
            )
            raise WorkspaceAccessDeniedError("Only the owner can create conversations in this workspace.")

        default_title = title or self.generate_default_title()

        conversation = self.conversation_repo.create(
            workspace_id=workspace_id,
            user_id=user_id,
            title=default_title,
            status=ConversationStatus.ACTIVE,
        )

        try:
            self.db.commit()
            self.db.refresh(conversation)
            logger.info(f"Conversation Created: {conversation.id} in workspace {workspace_id} by user {user_id}")
        except Exception:
            self.db.rollback()
            raise

        return conversation

    def get_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> Conversation:
        """
        Retrieves a conversation by ID and validates user access permissions.
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found.")

        self.validate_access(user_id, conversation)
        return conversation

    def list_conversations(
        self,
        workspace_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Conversation], int, int]:
        """
        Lists active (non-deleted) conversations in a workspace, paginated, sorted by last_message_at DESC.
        """
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(f"Workspace with ID {workspace_id} not found.")

        if workspace.owner_id != user_id:
            raise WorkspaceAccessDeniedError("Only the owner can list conversations in this workspace.")

        skip = (page - 1) * page_size
        limit = page_size

        # Count active conversations for workspace
        stmt = select(func.count(Conversation.id)).where(
            Conversation.workspace_id == workspace_id,
            Conversation.deleted_at.is_(None),
        )
        total = self.db.execute(stmt).scalar() or 0

        conversations = self.conversation_repo.list_by_workspace(
            workspace_id=workspace_id,
            limit=limit,
            offset=skip,
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return conversations, total, total_pages

    def rename_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
        new_title: str,
    ) -> Conversation:
        """
        Renames a conversation after validating ownership and length constraints.
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found.")

        self.validate_access(user_id, conversation)

        if not new_title or not new_title.strip():
            raise ValueError("Title cannot be empty")

        trimmed_title = new_title.strip()
        if len(trimmed_title) > 255:
            raise ValueError("Title cannot exceed 255 characters")

        conversation = self.conversation_repo.rename(conversation, trimmed_title)

        try:
            self.db.commit()
            self.db.refresh(conversation)
            logger.info(f"Conversation Renamed: {conversation.id} to '{trimmed_title}' by user {user_id}")
        except Exception:
            self.db.rollback()
            raise

        return conversation

    def archive_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> Conversation:
        """
        Archives a conversation. Archived conversations cannot accept new messages.
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found.")

        self.validate_access(user_id, conversation)

        conversation = self.conversation_repo.update(
            conversation,
            status=ConversationStatus.ARCHIVED,
        )

        try:
            self.db.commit()
            self.db.refresh(conversation)
            logger.info(f"Conversation Archived: {conversation.id} by user {user_id}")
        except Exception:
            self.db.rollback()
            raise

        return conversation

    def delete_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ) -> None:
        """
        Soft-deletes a conversation.
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found.")

        self.validate_access(user_id, conversation)

        self.conversation_repo.delete(conversation)

        try:
            self.db.commit()
            logger.info(f"Conversation Soft-Deleted: {conversation_id} by user {user_id}")
        except Exception:
            self.db.rollback()
            raise

    def touch_conversation(
        self,
        conversation_id: UUID,
        timestamp: datetime | None = None,
    ) -> Conversation:
        """
        Touches a conversation to update its last_message_at timestamp.
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found.")

        conversation = self.conversation_repo.update_last_message(conversation, timestamp)

        try:
            self.db.commit()
            self.db.refresh(conversation)
            logger.info(f"Conversation last_message_at updated: {conversation.id}")
        except Exception:
            self.db.rollback()
            raise

        return conversation
