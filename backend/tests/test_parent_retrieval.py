import unittest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.models.document_chunk import DocumentChunk
from app.retrieval.models import RetrievedChunk
from app.retrieval.retrievers.parent import ParentContextRetriever


class TestParentContextRetriever(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = self.SessionLocal()

        self.doc_id = uuid4()

        # Insert 3 document chunks
        self.chunk0 = DocumentChunk(
            id=uuid4(),
            document_id=self.doc_id,
            chunk_index=0,
            content="This is chunk index zero.",
            token_count=5,
            character_count=20,
            start_offset=0,
            end_offset=20,
        )
        self.chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=self.doc_id,
            chunk_index=1,
            content="This is chunk index one.",
            token_count=5,
            character_count=20,
            start_offset=21,
            end_offset=41,
        )
        self.chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=self.doc_id,
            chunk_index=2,
            content="This is chunk index two.",
            token_count=5,
            character_count=20,
            start_offset=42,
            end_offset=62,
        )
        self.db.add_all([self.chunk0, self.chunk1, self.chunk2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_expand_context_basic(self):
        # We start with retrieved chunk1 (index 1)
        retrieved = [
            RetrievedChunk(
                chunk_id=str(self.chunk1.id),
                document_id=str(self.doc_id),
                text=self.chunk1.content,
                score=0.9,
                page=0,
                chunk_index=1,
                metadata={},
            )
        ]

        # Expand with window_size = 1
        expanded = ParentContextRetriever.expand_context(
            self.db, retrieved, window_size=1
        )

        self.assertEqual(len(expanded), 1)
        expected_text = (
            "This is chunk index zero.\n\n"
            "This is chunk index one.\n\n"
            "This is chunk index two."
        )
        self.assertEqual(expanded[0].text, expected_text)

    def test_expand_context_boundary_low(self):
        # Retrieved chunk0 (index 0) - should not have chunk_index -1
        retrieved = [
            RetrievedChunk(
                chunk_id=str(self.chunk0.id),
                document_id=str(self.doc_id),
                text=self.chunk0.content,
                score=0.9,
                page=0,
                chunk_index=0,
                metadata={},
            )
        ]

        expanded = ParentContextRetriever.expand_context(
            self.db, retrieved, window_size=1
        )
        self.assertEqual(len(expanded), 1)
        expected_text = (
            "This is chunk index zero.\n\nThis is chunk index one."
        )
        self.assertEqual(expanded[0].text, expected_text)
