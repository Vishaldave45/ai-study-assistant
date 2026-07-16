import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.models.document import Document
from app.retrieval.service import RetrievalService
from app.prompts.builder import PromptBuilder
from app.llm.service import LLMService
from app.rag.exceptions import NoContextFound, GenerationFailed, RetrieverFailed, RAGException
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
        logger.info(f"RAGPipeline: Executing search for workspace {workspace_id}")
        try:
            search_response = self.retrieval_service.search(
                workspace_id=workspace_id,
                query=question,
            )
        except Exception as e:
            logger.error(f"RAGPipeline: Retriever query failed: {e}")
            raise RetrieverFailed(f"Retriever query failed: {str(e)}") from e

        if not search_response.results:
            logger.warning("RAGPipeline: No relevant chunks matched the threshold.")
            raise NoContextFound("No relevant context found.")

        # 2. Resolve document original filenames from DB
        doc_ids = {res.document_id for res in search_response.results}
        stmt = select(Document).where(Document.id.in_(doc_ids))
        docs = self.db.execute(stmt).scalars().all()
        doc_map = {doc.id: doc.original_filename for doc in docs}

        # 3. Format context chunks and citations
        chunks_for_builder = []
        citations = []
        for res in search_response.results:
            filename = doc_map.get(res.document_id, "Unknown Document")
            chunks_for_builder.append({
                "content": res.content,
                "filename": filename,
                "page": "N/A",
            })
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
