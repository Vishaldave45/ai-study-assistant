import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.document_chunk import DocumentChunk
from app.embedding.service import EmbeddingService
from app.retrieval.config import MAX_CONTEXT_CHUNKS, MIN_SCORE, TOP_K
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.schemas import SearchResponse, SearchResponseItem
from app.vectorstore.repository import VectorStoreRepository

logger = logging.getLogger(__name__)


class RetrievalService:

    def __init__(self, db: Session):
        self.db = db
        self.vector_repo = VectorStoreRepository(db)
        self.embedding_service = EmbeddingService()
        self.pipeline = RetrievalPipeline(self.vector_repo, self.embedding_service)

    def search(
        self,
        workspace_id: UUID,
        query: str,
        top_k: int = TOP_K,
        min_score: float = MIN_SCORE,
        max_chunks: int = MAX_CONTEXT_CHUNKS,
    ) -> SearchResponse:
        """
        Retrieves matching chunks for a user query in a workspace:
        1. Generates query embedding
        2. Performs FAISS search
        3. Filters by score and sorts
        4. Resolves text content from database
        5. Returns structured SearchResponse preserving ranking
        """
        # 1. Run pipeline
        results = self.pipeline.run_pipeline(
            workspace_id=workspace_id,
            query=query,
            top_k=top_k,
            min_score=min_score,
            max_chunks=max_chunks,
        )

        if not results:
            return SearchResponse(query=query, results=[])

        # 2. Resolve chunk content from DB
        chunk_ids = [res.chunk_id for res in results]
        stmt = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        db_chunks = self.db.execute(stmt).scalars().all()

        # Map chunk ID to its content
        chunk_map = {chunk.id: chunk.content for chunk in db_chunks}

        # 3. Preserve FAISS order and assemble response items
        response_items = []
        for res in results:
            content = chunk_map.get(res.chunk_id)
            if content is None:
                logger.warning(
                    f"Chunk content not found in database for chunk_id {res.chunk_id}"
                )
                continue
            response_items.append(
                SearchResponseItem(
                    chunk_id=res.chunk_id,
                    document_id=res.document_id,
                    score=res.score,
                    content=content,
                )
            )

        return SearchResponse(query=query, results=response_items)
