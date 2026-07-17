from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models.message_citation import MessageCitation
from app.repositories.base import BaseRepository


class MessageCitationRepository(BaseRepository[MessageCitation]):

    def bulk_create(
        self,
        citations: list[MessageCitation],
    ) -> list[MessageCitation]:
        for citation in citations:
            self.add(citation)
        self.flush()
        return citations

    def list_by_message(
        self,
        message_id: UUID,
    ) -> list[MessageCitation]:
        statement = (
            select(MessageCitation)
            .where(MessageCitation.message_id == message_id)
            .options(selectinload(MessageCitation.document_chunk))
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def delete_by_message(
        self,
        message_id: UUID,
    ) -> None:
        statement = select(MessageCitation).where(
            MessageCitation.message_id == message_id
        )
        result = self.db.execute(statement)
        citations = result.scalars().all()
        for citation in citations:
            super().delete(citation)
        self.flush()
