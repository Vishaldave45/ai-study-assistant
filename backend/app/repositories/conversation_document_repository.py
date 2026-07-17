from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.database.models.conversation_document import ConversationDocument
from app.database.models.document import Document
from app.repositories.base import BaseRepository


class ConversationDocumentRepository(BaseRepository[ConversationDocument]):

    def attach_document(
        self,
        conversation_id: UUID,
        document_id: UUID,
    ) -> ConversationDocument:
        relation = ConversationDocument(
            conversation_id=conversation_id,
            document_id=document_id,
        )
        self.add(relation)
        self.flush()
        return relation

    def detach_document(
        self,
        conversation_id: UUID,
        document_id: UUID,
    ) -> None:
        statement = select(ConversationDocument).where(
            ConversationDocument.conversation_id == conversation_id,
            ConversationDocument.document_id == document_id,
        )
        result = self.db.execute(statement)
        relation = result.scalar_one_or_none()
        if relation:
            super().delete(relation)
            self.flush()

    def list_documents(
        self,
        conversation_id: UUID,
    ) -> list[Document]:
        statement = (
            select(Document)
            .join(
                ConversationDocument,
                ConversationDocument.document_id == Document.id,
            )
            .where(
                ConversationDocument.conversation_id == conversation_id,
                Document.deleted_at.is_(None),
            )
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def exists(
        self,
        conversation_id: UUID,
        document_id: UUID,
    ) -> bool:
        statement = select(ConversationDocument).where(
            ConversationDocument.conversation_id == conversation_id,
            ConversationDocument.document_id == document_id,
        )
        return self.db.execute(statement).first() is not None
