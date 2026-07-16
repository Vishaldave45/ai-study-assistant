from __future__ import annotations

import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.enums import DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.embedding.service import EmbeddingService
from app.embedding.schemas import EmbeddingResult

logger = logging.getLogger(__name__)


class EmbeddingPipeline:

    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)
        self.chunks = ChunkRepository(db)
        self.embedding_service = EmbeddingService()

    def run_pipeline(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> list[EmbeddingResult]:
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise ValueError(f"Document with ID {document_id} not found.")

        logger.info(f"Embedding started for document {document_id}")
        document.status = DocumentStatus.EMBEDDING
        self.db.commit()

        try:
            # 1. Load active chunks from database
            chunk_records = self.chunks.list_by_document(document_id)
            if not chunk_records:
                logger.warning(f"No chunks found for document {document_id}.")
                document.status = DocumentStatus.EMBEDDED
                self.db.commit()
                return []

            chunk_texts = [c.content for c in chunk_records]

            # 2. Generate embeddings
            results = self.embedding_service.generate_embeddings(chunk_texts)

            # 3. Update status to EMBEDDED
            document.status = DocumentStatus.EMBEDDED
            self.db.commit()
            logger.info(f"Embedding finished for document {document_id}")
            return results

        except Exception as exc:
            self.db.rollback()
            document.status = DocumentStatus.FAILED
            self.db.commit()
            logger.error(f"Embedding failed for document {document_id}: {exc}")
            raise exc
