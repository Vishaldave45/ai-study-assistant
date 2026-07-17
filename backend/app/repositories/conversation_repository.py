from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.enums import ConversationStatus
from app.database.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):

    def create(
        self,
        workspace_id: UUID,
        user_id: UUID,
        title: str,
        status: ConversationStatus = ConversationStatus.ACTIVE,
        langgraph_thread_id: UUID | None = None,
    ) -> Conversation:
        conversation = Conversation(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            status=status,
            langgraph_thread_id=langgraph_thread_id,
        )
        self.add(conversation)
        self.flush()
        return conversation

    def get_by_id(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.deleted_at.is_(None),
            )
            .options(selectinload(Conversation.messages))
        )
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def list_by_workspace(
        self,
        workspace_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(
                Conversation.workspace_id == workspace_id,
                Conversation.deleted_at.is_(None),
            )
            .order_by(Conversation.last_message_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def list_by_user(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
            .order_by(Conversation.last_message_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def update(
        self,
        conversation: Conversation,
        **kwargs,
    ) -> Conversation:
        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        self.flush()
        return conversation

    def delete(
        self,
        conversation: Conversation,
    ) -> None:
        conversation.deleted_at = datetime.now(UTC)
        self.flush()

    def exists(
        self,
        conversation_id: UUID,
    ) -> bool:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None),
        )
        return self.db.execute(statement).first() is not None

    def update_last_message(
        self,
        conversation: Conversation,
        timestamp: datetime | None = None,
    ) -> Conversation:
        conversation.last_message_at = timestamp or datetime.now(UTC)
        self.flush()
        return conversation

    def rename(
        self,
        conversation: Conversation,
        new_title: str,
    ) -> Conversation:
        conversation.title = new_title
        self.flush()
        return conversation

    def get_thread_id(
        self,
        conversation_id: UUID,
    ) -> UUID | None:
        statement = select(Conversation.langgraph_thread_id).where(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None),
        )
        result = self.db.execute(statement)
        return result.scalar_one_or_none()
