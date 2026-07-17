import unittest
from unittest.mock import MagicMock
from app.llm.schemas import LLMResponse
from app.retrieval.models import RetrievedChunk
from app.retrieval.compression.compressor import ContextCompressor


class TestContextCompressor(unittest.TestCase):

    def test_compress_chunks(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            answer="Compressed dense summary.",
            model="gemini",
            finish_reason="STOP",
            usage={},
        )

        compressor = ContextCompressor(mock_llm)

        # A long chunk (> 50 words)
        long_text = (
            "Neural networks are computing systems inspired by the biological neural networks "
            "that constitute animal brains. Such systems learn to perform tasks by considering "
            "examples, generally without being programmed with task-specific rules. For example, "
            "in image recognition, they might learn to identify images that contain cats by "
            "analyzing example images that have been manually labeled as cat or no cat and "
            "using the results to identify cats in other images."
        )
        chunk1 = RetrievedChunk(
            chunk_id="chunk1",
            document_id="doc1",
            text=long_text,
            score=0.9,
            page=1,
            chunk_index=0,
        )

        # A short chunk (< 50 words) - should be skipped
        short_text = "Short text here."
        chunk2 = RetrievedChunk(
            chunk_id="chunk2",
            document_id="doc1",
            text=short_text,
            score=0.8,
            page=2,
            chunk_index=1,
        )

        compressed = compressor.compress_chunks([chunk1, chunk2])

        self.assertEqual(len(compressed), 2)

        # Chunk 1 should be compressed
        self.assertEqual(compressed[0].text, "Compressed dense summary.")
        self.assertEqual(compressed[0].chunk_id, "chunk1")
        self.assertEqual(compressed[0].document_id, "doc1")
        self.assertEqual(compressed[0].score, 0.9)

        # Chunk 2 should remain unchanged
        self.assertEqual(compressed[1].text, "Short text here.")
        self.assertEqual(compressed[1].chunk_id, "chunk2")

        # Verify generate was called exactly once (only for the long chunk)
        mock_llm.generate.assert_called_once()
