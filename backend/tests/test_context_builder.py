import unittest
from app.retrieval.models import RetrievedChunk
from app.retrieval.builders.context_builder import ContextBuilder


class TestContextBuilder(unittest.TestCase):

    def setUp(self):
        self.chunk1 = RetrievedChunk(
            chunk_id="chunk1",
            document_id="doc1",
            text="First chunk content",
            score=0.9,
            page=1,
            chunk_index=0,
        )
        self.chunk2 = RetrievedChunk(
            chunk_id="chunk2",
            document_id="doc1",
            text="Second chunk content",
            score=0.8,
            page=2,
            chunk_index=1,
        )
        # Duplicate of chunk1
        self.chunk1_dup = RetrievedChunk(
            chunk_id="chunk1",
            document_id="doc1",
            text="First chunk content duplicated",
            score=0.9,
            page=1,
            chunk_index=0,
        )
        self.chunk3 = RetrievedChunk(
            chunk_id="chunk3",
            document_id="doc2",
            text="Third chunk from another doc",
            score=0.7,
            page=0,
            chunk_index=0,
        )

        self.doc_map = {
            "doc1": "introduction.pdf",
            "doc2": "summary.pdf",
        }

    def test_deduplication(self):
        chunks = [self.chunk1, self.chunk1_dup, self.chunk2]
        context, citations, selected = ContextBuilder.build_context(
            chunks, self.doc_map, max_tokens=1000
        )
        # Only unique chunks should be selected
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0].chunk_id, "chunk1")
        self.assertEqual(selected[1].chunk_id, "chunk2")

    def test_citations_formatting(self):
        chunks = [self.chunk1, self.chunk3]
        context, citations, selected = ContextBuilder.build_context(
            chunks, self.doc_map, max_tokens=1000
        )
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0], "[1] introduction.pdf (Page 1)")
        self.assertEqual(citations[1], "[2] summary.pdf (Page 0)")

    def test_token_budget_truncation(self):
        # Setup a very small token budget so only the first chunk fits
        chunks = [self.chunk1, self.chunk2, self.chunk3]
        # First chunk alone has about 6 words/tokens. Let's set max_tokens=20 (enough for chunk1, but not chunk2)
        context, citations, selected = ContextBuilder.build_context(
            chunks, self.doc_map, max_tokens=20
        )
        # Check that it stops appending when budget is exceeded
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].chunk_id, "chunk1")
