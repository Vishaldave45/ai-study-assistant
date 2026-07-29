import asyncio
import logging
from typing import List, Dict, Any
from app.engine.chunker import SemanticChunk, ChunkType

logger = logging.getLogger(__name__)


class QueryPlanner:
    """
    Query Intent Planner determining which specialized retriever channels
    to activate based on query keywords and intent.
    """

    @staticmethod
    def plan_query(query: str) -> List[ChunkType]:
        query_lower = query.lower()
        active_types: set[ChunkType] = {"paragraph", "heading"}  # Always include core text

        # Check diagram intent
        if any(kw in query_lower for kw in ["diagram", "chart", "figure", "architecture", "flowchart", "draw"]):
            active_types.add("diagram")

        # Check table intent
        if any(kw in query_lower for kw in ["table", "column", "row", "data", "comparison", "list"]):
            active_types.add("table")

        # Check equation intent
        if any(kw in query_lower for kw in ["equation", "formula", "math", "latex", "calculate", "ratio"]):
            active_types.add("equation")

        return list(active_types)


class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion (RRF) deduplication and re-ranking algorithm.
    RRF Score = sum(1 / (k + rank_i)) across all retriever channels.
    """

    @staticmethod
    def fuse(results_by_channel: List[List[SemanticChunk]], top_k: int = 5, k: int = 60) -> List[SemanticChunk]:
        chunk_scores: Dict[str, Dict[str, Any]] = {}

        for channel_results in results_by_channel:
            for rank, chunk in enumerate(channel_results, start=1):
                # Unique identifier based on content and page
                chunk_key = f"p{chunk.page_number}_{hash(chunk.content)}"
                if chunk_key not in chunk_scores:
                    chunk_scores[chunk_key] = {"chunk": chunk, "score": 0.0}

                # Add RRF score contribution
                chunk_scores[chunk_key]["score"] += 1.0 / (k + rank)

        # Sort by accumulated RRF score descending
        sorted_entries = sorted(chunk_scores.values(), key=lambda x: x["score"], reverse=True)
        return [entry["chunk"] for entry in sorted_entries[:top_k]]


class HybridRAGOrchestrator:
    """
    Parallel Hybrid RAG Orchestrator running text, diagram, table, and equation
    retrievers concurrently and merging candidates using RRF.
    """

    def __init__(self, all_chunks: List[SemanticChunk]):
        self.all_chunks = all_chunks

    async def retrieve_parallel(self, query: str, top_k: int = 5) -> List[SemanticChunk]:
        """
        Executes query planning and fans out parallel retrieval tasks.
        """
        active_types = QueryPlanner.plan_query(query)
        logger.info(f"QueryPlanner activated channels for query '{query}': {active_types}")

        loop = asyncio.get_running_loop()

        # Define specialized filter tasks for each active chunk type
        async def fetch_channel_chunks(target_type: ChunkType) -> List[SemanticChunk]:
            # Simulate async vector channel search
            await asyncio.sleep(0.01)
            matching = [c for c in self.all_chunks if c.chunk_type == target_type or target_type in ["paragraph", "heading"]]
            # Rank by keyword overlap
            query_terms = set(query.lower().split())
            ranked = sorted(
                matching,
                key=lambda c: sum(1 for term in query_terms if term in c.content.lower()),
                reverse=True,
            )
            return ranked[:top_k]

        # Launch all active retriever channels concurrently
        channel_tasks = [fetch_channel_chunks(t) for t in active_types]
        channel_results = await asyncio.gather(*channel_tasks)

        # Fuse channel results using Reciprocal Rank Fusion
        fused_chunks = ReciprocalRankFusion.fuse(channel_results, top_k=top_k)
        return fused_chunks
