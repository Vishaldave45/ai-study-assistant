import logging
from uuid import UUID

from app.embedding.service import EmbeddingService
from app.retrieval.config import MAX_CONTEXT_CHUNKS, MIN_SCORE, TOP_K
from app.retrieval.exceptions import QueryEmbeddingError
from app.retrieval.filters import ResultFilter
from app.retrieval.ranking import ScoreRanker
from app.retrieval.retriever import FAISSRetriever
from app.vectorstore.repository import VectorStoreRepository
from app.vectorstore.schemas import SearchResult

logger = logging.getLogger(__name__)


class RetrievalPipeline:

    def __init__(
        self, vector_repo: VectorStoreRepository, embedding_service: EmbeddingService
    ):
        self.retriever = FAISSRetriever(vector_repo)
        self.embedding_service = embedding_service

    def run_pipeline(
        self,
        workspace_id: UUID,
        query: str,
        top_k: int = TOP_K,
        min_score: float = MIN_SCORE,
        max_chunks: int = MAX_CONTEXT_CHUNKS,
    ) -> list[SearchResult]:
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

        # 2. Search FAISS Vector Store
        # Retrieve candidate_limit to ensure we satisfy both constraints
        candidate_limit = max(top_k, max_chunks)
        results = self.retriever.retrieve(workspace_id, query_vector, candidate_limit)

        # 3. Apply Score Threshold Filtering
        filtered = ResultFilter.filter_by_score(results, min_score)

        # 4. Rank Results
        ranked = ScoreRanker.rank(filtered)

        # 5. Limit final results count
        final_limit = min(top_k, max_chunks)
        return ResultFilter.limit_results(ranked, final_limit)
