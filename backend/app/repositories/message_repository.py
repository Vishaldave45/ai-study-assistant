from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from app.database.enums import MessageRole
from app.database.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):

    def create(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.add(message)
        self.flush()
        return message

    def create_many(
        self,
        messages: list[Message],
    ) -> list[Message]:
        for message in messages:
            self.add(message)
        self.flush()
        return messages

    def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def last_messages(
        self,
        conversation_id: UUID,
        limit: int = 10,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def get(
        self,
        message_id: UUID,
    ) -> Message | None:
        statement = select(Message).where(Message.id == message_id)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def delete(
        self,
        message: Message,
    ) -> None:
        super().delete(message)
        self.flush()

    def count(
        self,
        conversation_id: UUID,
    ) -> int:
        statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        return self.db.execute(statement).scalar() or 0
