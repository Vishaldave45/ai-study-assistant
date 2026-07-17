from uuid import UUID
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from app.database.models.document_chunk import DocumentChunk
from app.retrieval.models import RetrievedChunk


class ParentContextRetriever:

    @staticmethod
    def expand_context(
        db: Session,
        chunks: list[RetrievedChunk],
        window_size: int = 1,
    ) -> list[RetrievedChunk]:
        """
        Expands each retrieved chunk's text to include neighboring chunks' text.
        Resolves neighbors from SQL database in a single grouped query.
        """
        if not chunks or window_size <= 0:
            return chunks

        conditions = []
        for chunk in chunks:
            doc_id = (
                UUID(chunk.document_id)
                if isinstance(chunk.document_id, str)
                else chunk.document_id
            )
            idx = chunk.chunk_index
            conditions.append(
                and_(
                    DocumentChunk.document_id == doc_id,
                    DocumentChunk.chunk_index >= max(0, idx - window_size),
                    DocumentChunk.chunk_index <= idx + window_size,
                )
            )

        stmt = select(DocumentChunk).where(or_(*conditions))
        db_chunks = db.execute(stmt).scalars().all()

        chunk_lookup = {}
        for db_chunk in db_chunks:
            key = (str(db_chunk.document_id), db_chunk.chunk_index)
            chunk_lookup[key] = db_chunk

        expanded_chunks = []
        for chunk in chunks:
            doc_id_str = str(chunk.document_id)
            idx = chunk.chunk_index

            neighbors = []
            for neighbor_idx in range(
                max(0, idx - window_size), idx + window_size + 1
            ):
                db_chunk = chunk_lookup.get((doc_id_str, neighbor_idx))
                if db_chunk:
                    neighbors.append(db_chunk)

            neighbors.sort(key=lambda x: x.chunk_index)
            expanded_text = "\n\n".join(n.content for n in neighbors)

            expanded_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    text=expanded_text,
                    score=chunk.score,
                    page=chunk.page,
                    chunk_index=chunk.chunk_index,
                    metadata=chunk.metadata,
                )
            )
        return expanded_chunks
