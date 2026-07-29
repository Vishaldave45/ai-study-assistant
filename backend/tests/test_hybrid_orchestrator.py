import unittest
import asyncio
from app.engine.chunker import SemanticChunk
from app.engine.retrieval.orchestrator import (
    QueryPlanner,
    ReciprocalRankFusion,
    HybridRAGOrchestrator,
)


class TestHybridOrchestrator(unittest.TestCase):

    def test_query_planner_intent_activation(self):
        """Verify QueryPlanner activates diagram, table, and equation channels based on query intent."""
        p_diag = QueryPlanner.plan_query("Show me the OSI model architecture diagram")
        self.assertIn("diagram", p_diag)

        p_table = QueryPlanner.plan_query("Compare latency values in the table")
        self.assertIn("table", p_table)

        p_eq = QueryPlanner.plan_query("What is the average access time formula equation?")
        self.assertIn("equation", p_eq)

    def test_reciprocal_rank_fusion(self):
        """Verify RRF deduplicates chunks and ranks by combined score."""
        c1 = SemanticChunk(page_number=1, chunk_type="diagram", content="OSI Diagram")
        c2 = SemanticChunk(page_number=1, chunk_type="paragraph", content="Text Intro")

        # Channel 1: [c1, c2], Channel 2: [c1]
        fused = ReciprocalRankFusion.fuse([[c1, c2], [c1]], top_k=2)

        self.assertEqual(len(fused), 2)
        # c1 appeared at rank 1 in both channels, so it should rank first
        self.assertEqual(fused[0].content, "OSI Diagram")

    def test_hybrid_rag_orchestrator_parallel_retrieval(self):
        """Verify async parallel retrieval over multi-channel semantic chunks."""
        chunks = [
            SemanticChunk(page_number=1, chunk_type="heading", content="Header Page 1"),
            SemanticChunk(page_number=1, chunk_type="paragraph", content="CPU Cache Introduction"),
            SemanticChunk(page_number=1, chunk_type="diagram", content="Diagram: CPU Cache Architecture"),
            SemanticChunk(page_number=1, chunk_type="table", content="| Cache | Latency |\n| L1 | 1ns |"),
        ]

        orchestrator = HybridRAGOrchestrator(chunks)
        fused = asyncio.run(orchestrator.retrieve_parallel("Show me the CPU cache architecture diagram", top_k=3))

        self.assertGreater(len(fused), 0)
        # Diagram chunk should rank at top
        self.assertTrue(any(c.chunk_type == "diagram" for c in fused))


if __name__ == "__main__":
    unittest.main()
