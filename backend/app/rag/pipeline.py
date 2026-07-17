import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.models.document import Document
from app.retrieval.service import RetrievalService
from app.prompts.builder import PromptBuilder
from app.llm.service import LLMService
from app.rag.exceptions import (
    NoContextFound,
    GenerationFailed,
    RetrieverFailed,
    RAGException,
)
from app.rag.citations import CitationFormatter

logger = logging.getLogger(__name__)


class RAGPipeline:

    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.prompt_builder = PromptBuilder()
        self.llm_service = LLMService(provider_type="gemini")

    def answer_question(self, workspace_id: UUID, question: str) -> dict:
        """
        Coordinates the pipeline: retrieval -> prompt building -> LLM generation.
        """
        # 1. Retrieve chunks
        logger.info(f"RAGPipeline: Executing retrieve for workspace {workspace_id}")
        try:
            retrieval = self.retrieval_service.retrieve(
                workspace_id=workspace_id,
                query=question,
            )
        except Exception as e:
            logger.error(f"RAGPipeline: Retriever query failed: {e}")
            raise RetrieverFailed(f"Retriever query failed: {str(e)}") from e

        if not retrieval.chunks:
            logger.warning("RAGPipeline: No relevant chunks matched.")
            raise NoContextFound("No relevant context found.")

        # 2. Format context chunks and citations using pre-resolved metadata
        chunks_for_builder = []
        citations = []
        for res in retrieval.chunks:
            filename = res.metadata.get("original_filename", "Unknown Document")
            chunks_for_builder.append(
                {
                    "content": res.text,
                    "filename": filename,
                    "page": "N/A",
                }
            )
            citation = CitationFormatter.format_citation(
                filename=filename,
                score=res.score,
                page="N/A",
            )
            citations.append(citation)

        # 4. Compile the prompt
        logger.info("RAGPipeline: Structuring prompt text")
        try:
            prompt = self.prompt_builder.build(question, chunks_for_builder)
        except Exception as e:
            logger.error(f"RAGPipeline: Failed to construct prompt: {e}")
            raise RAGException(f"Prompt building failed: {str(e)}") from e

        # 5. Send to LLM
        logger.info("RAGPipeline: Requesting generation from LLM layer")
        try:
            llm_response = self.llm_service.generate(prompt)
        except Exception as e:
            logger.error(f"RAGPipeline: LLM invocation failed: {e}")
            raise GenerationFailed(f"LLM service unavailable: {str(e)}") from e

        return {
            "answer": llm_response.answer,
            "citations": citations,
            "chunks_used": len(chunks_for_builder),
            "model": llm_response.model,
        }
