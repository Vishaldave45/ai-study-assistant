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
            # Try auto-indexing workspace documents if vectors haven't been generated
            try:
                from app.database.models.document import Document
                docs_stmt = select(Document).where(
                    Document.workspace_id == workspace_id, 
                    Document.deleted_at.is_(None)
                )
                docs = self.db.execute(docs_stmt).scalars().all()
                for doc in docs:
                    try:
                        self.vectorstore_service.index_document(doc.owner_id, doc.id)
                    except Exception as idx_err:
                        logger.warning(f"Auto-indexing doc {doc.id} failed during retrieval: {idx_err}")

                # Retry vector search
                results = self.vectorstore_service.search_workspace(
                    workspace_id=workspace_id,
                    query_vector=query_vector,
                    top_k=fetch_k,
                )
            except Exception as e:
                logger.warning(f"Auto-indexing fallback failed: {e}")

        if not results:
            # Fallback to direct DB chunks for workspace documents
            try:
                from app.database.models.document import Document
                chunk_stmt = (
                    select(DocumentChunk, Document)
                    .join(Document, DocumentChunk.document_id == Document.id)
                    .where(Document.workspace_id == workspace_id, Document.deleted_at.is_(None))
                    .limit(fetch_k)
                )
                db_results = self.db.execute(chunk_stmt).all()
                fallback_chunks = []
                for chunk_obj, doc_obj in db_results:
                    fallback_chunks.append(
                        RetrievedChunk(
                            chunk_id=str(chunk_obj.id),
                            document_id=str(doc_obj.id),
                            text=chunk_obj.content,
                            score=0.8,
                            page=0,
                            chunk_index=chunk_obj.chunk_index,
                            metadata={"original_filename": doc_obj.original_filename},
                        )
                    )
                return fallback_chunks
            except Exception as e:
                logger.error(f"Fallback DB chunk retrieval failed: {e}")
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
