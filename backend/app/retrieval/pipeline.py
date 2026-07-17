import logging
from uuid import UUID
from sqlalchemy import select
from app.database.models.document import Document
from app.retrieval.models import RetrievedChunk
from app.retrieval.retrievers.semantic import SemanticRetriever
from app.embedding.service import EmbeddingService
from app.vectorstore.service import VectorStoreService
from app.llm.service import LLMService
from app.retrieval.config import MIN_SCORE

logger = logging.getLogger(__name__)


class RetrievalPipeline:

    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        embedding_service: EmbeddingService,
        vectorstore_service: VectorStoreService,
        llm_service: LLMService,
    ):
        self.semantic_retriever = semantic_retriever
        self.embedding_service = embedding_service
        self.vectorstore_service = vectorstore_service
        self.llm_service = llm_service

    def run(
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
    ) -> tuple[list[RetrievedChunk], str, list[str]]:
        if not query:
            return [], "", []

        # 0. Apply query rewriting if history is present
        search_query = query
        if history:
            from app.retrieval.rewriting.query_rewriter import QueryRewriter

            rewriter = QueryRewriter(self.llm_service)
            search_query = rewriter.rewrite(query, history)
            logger.info(
                f"QueryRewriter: Rewrote query '{query}' to '{search_query}'"
            )

        # 1. Retrieve candidates using rewritten query. If MMR is used, fetch more candidates.
        fetch_k = max(20, top_k * 3) if use_mmr else top_k
        chunks = self.semantic_retriever.retrieve(
            workspace_id=workspace_id,
            query=search_query,
            fetch_k=fetch_k,
        )

        if not chunks:
            return [], "", []

        # 2. Apply Threshold Filtering
        from app.retrieval.ranking.threshold import ThresholdFilter

        chunks = ThresholdFilter.filter_by_score(chunks, min_score)

        if not chunks:
            return [], "", []

        # 3. Apply MMR if requested
        if use_mmr:
            try:
                embeddings = self.embedding_service.generate_embeddings(
                    [search_query]
                )
                if embeddings:
                    query_embedding = embeddings[0].vector
                    chunk_ids = [UUID(c.chunk_id) for c in chunks]
                    chunk_embeddings = self.vectorstore_service.get_vectors(
                        workspace_id, chunk_ids
                    )

                    from app.retrieval.ranking.mmr import MMRRanker

                    chunks = MMRRanker.rank(
                        query_embedding=query_embedding,
                        chunks=chunks,
                        chunk_embeddings={
                            str(k): v for k, v in chunk_embeddings.items()
                        },
                        lambda_val=lambda_val,
                        top_k=top_k,
                    )
            except Exception as e:
                logger.error(f"MMR ranking failed, falling back to top_k: {e}")
                chunks = chunks[:top_k]
        else:
            chunks = chunks[:top_k]

        # 4. Apply Parent Context Expansion if requested
        if use_parent and parent_window_size > 0:
            from app.retrieval.retrievers.parent import ParentContextRetriever

            chunks = ParentContextRetriever.expand_context(
                db=self.semantic_retriever.db,
                chunks=chunks,
                window_size=parent_window_size,
            )

        # 4.5 Apply Context Compression if requested
        if use_compression:
            from app.retrieval.compression.compressor import ContextCompressor

            compressor = ContextCompressor(self.llm_service)
            chunks = compressor.compress_chunks(chunks)

        # 5. Resolve document metadata from DB
        doc_ids = {
            UUID(c.document_id) if isinstance(c.document_id, str) else c.document_id
            for c in chunks
        }
        doc_map = {}
        if doc_ids:
            stmt = select(Document).where(Document.id.in_(doc_ids))
            docs = self.semantic_retriever.db.execute(stmt).scalars().all()
            doc_map = {str(doc.id): doc.original_filename for doc in docs}

        # 6. Build context & citations respecting the token budget
        from app.retrieval.builders.context_builder import ContextBuilder

        context_text, citations, selected_chunks = ContextBuilder.build_context(
            chunks=chunks, doc_map=doc_map, max_tokens=max_tokens
        )

        return selected_chunks, context_text, citations
