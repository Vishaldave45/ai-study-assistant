import logging
from app.llm.service import LLMService
from app.retrieval.models import RetrievedChunk

logger = logging.getLogger(__name__)


class ContextCompressor:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def compress_chunks(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """
        Compresses long RetrievedChunk texts using LLM summarization.
        """
        if not chunks:
            return []

        compressed_chunks = []
        for chunk in chunks:
            words = chunk.text.split()
            # If the chunk is short, skip summarization to save time and tokens
            if len(words) < 50:
                compressed_chunks.append(chunk)
                continue

            prompt = (
                "You are an expert summarizer. Compress the following document chunk text into a shorter, "
                "dense summary of its core facts. Maintain the factual accuracy and key details.\n\n"
                f"Text: {chunk.text}\n\n"
                "Summary:"
            )
            try:
                response = self.llm_service.generate(prompt)
                summary = response.answer.strip()
                if summary:
                    compressed_chunks.append(
                        RetrievedChunk(
                            chunk_id=chunk.chunk_id,
                            document_id=chunk.document_id,
                            text=summary,
                            score=chunk.score,
                            page=chunk.page,
                            chunk_index=chunk.chunk_index,
                            metadata=chunk.metadata,
                        )
                    )
                else:
                    compressed_chunks.append(chunk)
            except Exception as e:
                logger.error(f"Failed to compress chunk {chunk.chunk_id}: {e}")
                compressed_chunks.append(chunk)
        return compressed_chunks
