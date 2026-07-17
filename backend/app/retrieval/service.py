from uuid import UUID
from sqlalchemy.orm import Session
from app.retrieval.models import RetrievalResult
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.retrievers.semantic import SemanticRetriever
from app.embedding.service import EmbeddingService
from app.vectorstore.service import VectorStoreService
from app.llm.service import LLMService
from app.retrieval.config import MIN_SCORE


class RetrievalService:

    def __init__(
        self,
        db: Session | None = None,
        pipeline: RetrievalPipeline | None = None,
    ):
        if pipeline is not None:
            self.pipeline = pipeline
        elif db is not None:
            embedding_service = EmbeddingService()
            vectorstore_service = VectorStoreService(db)
            llm_service = LLMService()
            semantic_retriever = SemanticRetriever(
                db=db,
                embedding_service=embedding_service,
                vectorstore_service=vectorstore_service,
            )
            self.pipeline = RetrievalPipeline(
                semantic_retriever=semantic_retriever,
                embedding_service=embedding_service,
                vectorstore_service=vectorstore_service,
                llm_service=llm_service,
            )
        else:
            raise ValueError("Either db or pipeline must be provided.")

    def retrieve(
        self,
        workspace_id: UUID,
        query: str,
        history: list | None = None,
        use_mmr: bool = False,
        lambda_val: float = 0.5,
        min_score: float = MIN_SCORE,
        use_parent: bool = False,
        parent_window_size: int = 1,
        use_compression: bool = False,
        top_k: int = 5,
        max_tokens: int = 4000,
    ) -> RetrievalResult:
        chunks, context_text, citations = self.pipeline.run(
            workspace_id=workspace_id,
            query=query,
            history=history,
            use_mmr=use_mmr,
            lambda_val=lambda_val,
            min_score=min_score,
            use_parent=use_parent,
            parent_window_size=parent_window_size,
            use_compression=use_compression,
            top_k=top_k,
            max_tokens=max_tokens,
        )
        return RetrievalResult(
            query=query,
            chunks=chunks,
            context_text=context_text,
            citations=citations,
        )
