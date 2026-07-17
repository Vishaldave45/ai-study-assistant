from __future__ import annotations

from uuid import UUID
from sqlalchemy import select, delete, func

from app.database.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[DocumentChunk]):

    def create(
        self,
        document_id: UUID,
        chunk_index: int,
        content: str,
        token_count: int,
        character_count: int,
        start_offset: int,
        end_offset: int,
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            token_count=token_count,
            character_count=character_count,
            start_offset=start_offset,
            end_offset=end_offset,
        )
        self.add(chunk)
        return chunk

    def bulk_add(self, chunks: list[DocumentChunk]) -> None:
        self.db.add_all(chunks)
        self.flush()

    def list_by_document(self, document_id: UUID) -> list[DocumentChunk]:
        statement = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def delete_all(self, document_id: UUID) -> None:
        statement = delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
        self.db.execute(statement)
        self.flush()

    def count(self, document_id: UUID) -> int:
        statement = select(func.count(DocumentChunk.id)).where(
            DocumentChunk.document_id == document_id
        )
        return self.db.execute(statement).scalar() or 0
