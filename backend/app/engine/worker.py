import asyncio
import logging
from typing import Callable, Optional
from pydantic import BaseModel
from app.engine.factory import DocumentProcessorFactory
from app.engine.builder import MarkdownBuilder
from app.engine.chunker import SmartSemanticChunker, SemanticChunk

logger = logging.getLogger(__name__)


class IngestProgress(BaseModel):
    stage: str
    percentage: int
    total_pages: int
    processed_pages: int
    error: Optional[str] = None


class AsyncIngestWorker:
    """
    Asynchronous Document Ingestion Worker processing multi-page document parsing,
    vision AI extraction, semantic chunking, and progress callback notifications.
    """

    @classmethod
    async def process_document_async(
        cls,
        file_bytes: bytes,
        filename: str = "document.pdf",
        progress_callback: Optional[Callable[[IngestProgress], None]] = None,
    ) -> list[SemanticChunk]:
        """
        Asynchronously parses PDF, extracts PageObjects, generates semantic chunks,
        and reports progress updates.
        """
        # 1. Stage 1: Parse PageObjects (10%)
        if progress_callback:
            progress_callback(
                IngestProgress(
                    stage="Extracting PageObjects via PyMuPDF",
                    percentage=10,
                    total_pages=0,
                    processed_pages=0,
                )
            )

        processor = DocumentProcessorFactory.get_processor(filename)
        loop = asyncio.get_running_loop()

        # Run CPU-bound PyMuPDF parsing in thread executor
        page_objects = await loop.run_in_executor(None, processor.process, file_bytes)
        total_pages = len(page_objects)

        # 2. Stage 2: Vision Analysis Progress (50%)
        if progress_callback:
            progress_callback(
                IngestProgress(
                    stage="Extracting Page Objects & Text Blocks",
                    percentage=50,
                    total_pages=total_pages,
                    processed_pages=total_pages,
                )
            )

        # 3. Stage 3: Semantic Chunking (80%)
        chunks = await loop.run_in_executor(None, SmartSemanticChunker.chunk_document, page_objects)

        if progress_callback:
            progress_callback(
                IngestProgress(
                    stage="Building Semantic Chunks & Indexing",
                    percentage=80,
                    total_pages=total_pages,
                    processed_pages=total_pages,
                )
            )

        # 4. Stage 4: Ingestion Complete (100%)
        if progress_callback:
            progress_callback(
                IngestProgress(
                    stage="Ready",
                    percentage=100,
                    total_pages=total_pages,
                    processed_pages=total_pages,
                )
            )

        return chunks
