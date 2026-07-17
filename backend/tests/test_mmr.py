import unittest
from app.retrieval.models import RetrievedChunk
from app.retrieval.ranking.mmr import MMRRanker


class TestMMR(unittest.TestCase):

    def setUp(self):
        # Query: [1.0, 0.0]
        self.query_emb = [1.0, 0.0]

        # Chunks:
        # C1: [1.0, 0.0] (Perfect match)
        # C2: [0.99, 0.01] (Very high relevance, very similar to C1)
        # C3: [0.0, 1.0] (Lower relevance, but orthogonal/diverse compared to C1)
        self.chunk1 = RetrievedChunk(
            chunk_id="chunk1",
            document_id="doc1",
            text="chunk1 text",
            score=0.99,
            page=0,
            chunk_index=0,
        )
        self.chunk2 = RetrievedChunk(
            chunk_id="chunk2",
            document_id="doc1",
            text="chunk2 text",
            score=0.98,
            page=0,
            chunk_index=1,
        )
        self.chunk3 = RetrievedChunk(
            chunk_id="chunk3",
            document_id="doc1",
            text="chunk3 text",
            score=0.1,
            page=0,
            chunk_index=2,
        )

        self.chunks = [self.chunk1, self.chunk2, self.chunk3]
        self.chunk_embeddings = {
            "chunk1": [1.0, 0.0],
            "chunk2": [0.99, 0.01],
            "chunk3": [0.0, 1.0],
        }

    def test_mmr_pure_relevance(self):
        # With lambda = 1.0, MMR should select chunk1, then chunk2 (highest relevance)
        ranked = MMRRanker.rank(
            query_embedding=self.query_emb,
            chunks=self.chunks,
            chunk_embeddings=self.chunk_embeddings,
            lambda_val=1.0,
            top_k=2,
        )
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].chunk_id, "chunk1")
        self.assertEqual(ranked[1].chunk_id, "chunk2")

    def test_mmr_diversity(self):
        # With lambda = 0.4, selecting the second item should penalize chunk2 (highly similar to chunk1)
        # and prefer chunk3 (lower relevance but highly diverse/orthogonal)
        ranked = MMRRanker.rank(
            query_embedding=self.query_emb,
            chunks=self.chunks,
            chunk_embeddings=self.chunk_embeddings,
            lambda_val=0.4,
            top_k=2,
        )
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].chunk_id, "chunk1")
        self.assertEqual(ranked[1].chunk_id, "chunk3")

    def test_mmr_empty_edge_cases(self):
        ranked = MMRRanker.rank(
            query_embedding=self.query_emb,
            chunks=[],
            chunk_embeddings={},
            lambda_val=0.5,
            top_k=2,
        )
        self.assertEqual(ranked, [])

        ranked = MMRRanker.rank(
            query_embedding=self.query_emb,
            chunks=self.chunks,
            chunk_embeddings=self.chunk_embeddings,
            lambda_val=0.5,
            top_k=0,
        )
        self.assertEqual(ranked, [])
