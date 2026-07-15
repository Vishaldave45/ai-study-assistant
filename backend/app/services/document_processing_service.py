from __future__ import annotations

import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.enums import DocumentStatus
from app.database.models.document_chunk import DocumentChunk
from app.exceptions.document import DocumentNotFoundError
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.services.document_service import DocumentService
from app.pdf.parser import PDFParser
from app.text.pipeline import TextProcessingPipeline
from app.chunking.pipeline import ChunkingPipeline

logger = logging.getLogger(__name__)


class DocumentProcessingService:

    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)
        self.chunks = ChunkRepository(db)
        self.document_service = DocumentService(db)

    def process_document(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> int:
        """
        Process the document: Parse, Clean, Chunk, and Save to database.
        Returns the number of chunks created.
        """
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found.")

        # Update status to PROCESSING
        document.status = DocumentStatus.PROCESSING
        self.db.commit()

        try:
            # 1. Load file stream
            stream = self.document_service.get_document_stream(
                owner_id=owner_id,
                document_id=document_id,
            )

            # 2. Parse PDF to get raw text
            parsed_pdf = PDFParser.parse(stream.getvalue())

            # Update document page count if not set
            if parsed_pdf.page_count:
                document.page_count = parsed_pdf.page_count

            # 3. Clean and normalize text
            processed = TextProcessingPipeline.process(parsed_pdf.text)

            # 4. Split text into chunks
            pipeline = ChunkingPipeline()
            chunk_schemas = pipeline.chunk_text(processed.text)

            # 5. Clear previous chunks if any (reprocessing safety)
            self.chunks.delete_all(document_id)

            # 6. Bulk add new chunks
            chunk_models = []
            for schema in chunk_schemas:
                chunk_models.append(
                    DocumentChunk(
                        document_id=document_id,
                        chunk_index=schema.index,
                        content=schema.content,
                        token_count=schema.token_count,
                        character_count=schema.character_count,
                        start_offset=schema.start_offset,
                        end_offset=schema.end_offset,
                    )
                )

            if chunk_models:
                self.chunks.bulk_add(chunk_models)

            # 7. Update status to READY
            document.status = DocumentStatus.READY
            self.db.commit()
            logger.info(
                f"Successfully processed document {document_id}. "
                f"Created {len(chunk_models)} chunks."
            )
            return len(chunk_models)

        except Exception as exc:
            self.db.rollback()
            document.status = DocumentStatus.FAILED
            self.db.commit()
            logger.error(f"Failed to process document {document_id}: {exc}")
            raise exc
