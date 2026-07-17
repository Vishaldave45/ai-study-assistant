import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models.document_chunk import DocumentChunk
from app.embedding.service import EmbeddingService
from app.vectorstore.service import VectorStoreService
from app.retrieval.models import RetrievedChunk
from app.retrieval.exceptions import QueryEmbeddingError

logger = logging.getLogger(__name__)


class SemanticRetriever:

    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
        vectorstore_service: VectorStoreService,
    ):
        self.db = db
        self.embedding_service = embedding_service
        self.vectorstore_service = vectorstore_service

    def retrieve(
        self,
        workspace_id: UUID,
        query: str,
        fetch_k: int = 20,
    ) -> list[RetrievedChunk]:
        if not query:
            return []

        # 1. Generate query embedding
        try:
            embeddings = self.embedding_service.generate_embeddings([query])
            if not embeddings:
                raise QueryEmbeddingError("No embedding was generated for the query.")
            query_vector = embeddings[0].vector
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise QueryEmbeddingError(f"Failed to generate query embedding: {e}") from e

        # 2. Perform vectorstore similarity search
        results = self.vectorstore_service.search_workspace(
            workspace_id=workspace_id,
            query_vector=query_vector,
            top_k=fetch_k,
        )

        if not results:
            return []

        # 3. Resolve actual chunk content from SQL DB
        chunk_ids = [res.chunk_id for res in results]
        stmt = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        db_chunks = self.db.execute(stmt).scalars().all()
        chunk_map = {chunk.id: chunk for chunk in db_chunks}

        # 4. Assemble RetrievedChunk list preserving vector search rank order
        chunks = []
        for item in results:
            db_chunk = chunk_map.get(item.chunk_id)
            if db_chunk is None:
                logger.warning(
                    f"Chunk content not found in database for chunk_id {item.chunk_id}"
                )
                continue
            chunks.append(
                RetrievedChunk(
                    chunk_id=str(item.chunk_id),
                    document_id=str(item.document_id),
                    text=db_chunk.content,
                    score=item.score,
                    page=0,  # Default fallback as pages are not stored in chunks table
                    chunk_index=db_chunk.chunk_index,
                    metadata={},
                )
            )
        return chunks
