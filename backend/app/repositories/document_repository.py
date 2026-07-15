from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.database.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):

    def get_by_id(
        self,
        document_id: UUID,
    ) -> Document | None:
        statement = (
            select(Document)
            .where(
                Document.id == document_id,
                Document.deleted_at.is_(None),
            )
        )
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def list_by_workspace(
        self,
        workspace_id: UUID,
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.deleted_at.is_(None),
            )
            .order_by(Document.created_at.asc())
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def exists(
        self,
        document_id: UUID,
    ) -> bool:
        statement = (
            select(Document)
            .where(
                Document.id == document_id,
                Document.deleted_at.is_(None),
            )
        )
        return self.db.execute(statement).first() is not None

    def delete(
        self,
        document: Document,
    ) -> None:
        document.deleted_at = datetime.now(UTC)
        self.flush()

    def count(
        self,
        workspace_id: UUID,
        query: str | None = None,
    ) -> int:
        statement = (
            select(func.count(Document.id))
            .where(
                Document.workspace_id == workspace_id,
                Document.deleted_at.is_(None),
            )
        )

        if query:
            statement = statement.where(
                Document.original_filename.ilike(f"%{query}%")
            )

        return self.db.execute(statement).scalar() or 0

    def paginate(
        self,
        workspace_id: UUID,
        skip: int = 0,
        limit: int = 100,
        query: str | None = None,
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.deleted_at.is_(None),
            )
            .order_by(Document.created_at.asc())
        )

        if query:
            statement = statement.where(
                Document.original_filename.ilike(f"%{query}%")
            )

        statement = statement.offset(skip).limit(limit)
        result = self.db.execute(statement)
        return list(result.scalars().all())
