import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.document_processing_service import DocumentProcessingService
from app.embedding.pipeline import EmbeddingPipeline
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.vectorstore.repository import VectorStoreRepository
from app.vectorstore.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStoreService:

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.vector_repo = VectorStoreRepository(db)

    def index_document(self, owner_id: UUID, document_id: UUID) -> dict:
        """
        Runs the complete pipeline for a document:
        Document -> Chunks -> Embeddings -> FAISS -> Save.
        """
        document = self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")

        workspace_id = document.workspace_id

        # 1. Chunk document (will re-chunk if chunks already exist)
        processing_service = DocumentProcessingService(self.db)
        chunks_count = processing_service.process_document(owner_id, document_id)

        # Retrieve chunks
        chunks = self.chunk_repo.list_by_document(document_id)
        if not chunks:
            raise VectorStoreError(f"No chunks were generated for document {document_id}")

        # 2. Generate embeddings
        embedding_pipeline = EmbeddingPipeline(self.db)
        embedding_results = embedding_pipeline.run_pipeline(owner_id, document_id)
        if not embedding_results:
            raise VectorStoreError(f"No embeddings were generated for document {document_id}")

        # 3. Save to FAISS vector store
        # Delete old vectors first for clean re-indexing
        self.vector_repo.delete_document_vectors(workspace_id, document_id)

        # Prepare vectors and metadata
        vectors = [res.vector for res in embedding_results]

        # Match chunks to their metadata in order
        metadata = []
        for chunk in chunks:
            metadata.append({
                "chunk_id": chunk.id,
                "document_id": document_id,
            })

        # Add vectors
        self.vector_repo.add_vectors(workspace_id, vectors, metadata)

        # Return statistics
        return {
            "chunks": chunks_count,
            "vectors": len(vectors),
            "dimension": len(vectors[0]) if vectors else 384
        }

    def search_workspace(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int = 5,
    ):
        """Perform similarity search on workspace index."""
        return self.vector_repo.search_vectors(workspace_id, query_vector, top_k)

    def delete_document_vectors(self, workspace_id: UUID, document_id: UUID) -> None:
        """Delete document vectors from index."""
        self.vector_repo.delete_document_vectors(workspace_id, document_id)
