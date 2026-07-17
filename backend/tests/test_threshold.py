import unittest
from app.retrieval.models import RetrievedChunk
from app.retrieval.ranking.threshold import ThresholdFilter


class TestThresholdFilter(unittest.TestCase):

    def setUp(self):
        self.chunk1 = RetrievedChunk(
            chunk_id="chunk1",
            document_id="doc1",
            text="text1",
            score=0.9,
            page=0,
            chunk_index=0,
        )
        self.chunk2 = RetrievedChunk(
            chunk_id="chunk2",
            document_id="doc1",
            text="text2",
            score=0.5,
            page=0,
            chunk_index=1,
        )
        self.chunk3 = RetrievedChunk(
            chunk_id="chunk3",
            document_id="doc1",
            text="text3",
            score=0.3,
            page=0,
            chunk_index=2,
        )
        self.chunks = [self.chunk1, self.chunk2, self.chunk3]

    def test_filter_by_score_basic(self):
        # Only chunks with score >= 0.5 should pass
        filtered = ThresholdFilter.filter_by_score(self.chunks, 0.5)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].chunk_id, "chunk1")
        self.assertEqual(filtered[1].chunk_id, "chunk2")

    def test_filter_by_score_high_threshold(self):
        # Threshold higher than any score
        filtered = ThresholdFilter.filter_by_score(self.chunks, 0.95)
        self.assertEqual(filtered, [])

    def test_filter_by_score_low_threshold(self):
        # Threshold lower than all scores
        filtered = ThresholdFilter.filter_by_score(self.chunks, 0.1)
        self.assertEqual(len(filtered), 3)
