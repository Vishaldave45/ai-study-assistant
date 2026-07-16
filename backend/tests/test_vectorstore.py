import unittest
import tempfile
import numpy as np
from uuid import uuid4
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.enums import UserStatus, DocumentStatus

from app.vectorstore.faiss_store import FAISSVectorStore
from app.vectorstore.metadata_store import MetadataStore
from app.vectorstore.exceptions import (
    IndexNotFoundError,
    DimensionMismatchError,
    SearchError,
    VectorStoreError,
)
from app.vectorstore.schemas import SearchResult
from app.vectorstore.service import VectorStoreService
from app.vectorstore.config import VECTOR_DIMENSION

# Set up testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_vectorstore_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class TestVectorStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()

        # Set up a temporary directory for vector storage to isolate tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patcher1 = patch("app.vectorstore.faiss_store.STORAGE_DIR", self.temp_dir.name)
        self.patcher1.start()

        self.store = FAISSVectorStore()
        self.workspace_id = uuid4()
        self.document_id = uuid4()

        # Seed database models for service testing
        self.user_id = uuid4()
        user = User(
            id=self.user_id,
            email=f"vector_user_{uuid4().hex[:6]}@example.com",
            full_name="Vector Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(user)

        self.workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Vector Workspace",
        )
        self.db.add(self.workspace)

        self.document = Document(
            id=self.document_id,
            workspace_id=self.workspace_id,
            original_filename="vector_test.pdf",
            stored_filename="stored_vector_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.document)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.patcher1.stop()
        self.temp_dir.cleanup()

    def test_create_and_load_workspace_index(self):
        # Create a new index in memory
        self.store.create(self.workspace_id)
        
        # Save it to disk
        self.store.save(self.workspace_id)

        # Check files exist
        workspace_dir = Path(self.temp_dir.name) / str(self.workspace_id)
        self.assertTrue((workspace_dir / "index.faiss").exists())
        self.assertTrue((workspace_dir / "metadata.pkl").exists())

        # Clear memory cache in store
        self.store._cache.clear()

        # Load it back
        self.store.load(self.workspace_id)
        self.assertIn(self.workspace_id, self.store._cache)

    def test_load_nonexistent_index_raises_error(self):
        random_id = uuid4()
        with self.assertRaises(IndexNotFoundError):
            self.store.load(random_id)

    def test_add_and_search_vectors(self):
        self.store.create(self.workspace_id)

        # Create dummy vectors and metadata
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        
        # 384-dimensional vectors
        vec1 = [0.1] * VECTOR_DIMENSION
        vec2 = [0.5] * VECTOR_DIMENSION

        vectors = [vec1, vec2]
        metadata = [
            {"chunk_id": chunk_id1, "document_id": self.document_id},
            {"chunk_id": chunk_id2, "document_id": self.document_id},
        ]

        self.store.add(self.workspace_id, vectors, metadata)

        # Query vector close to vec2
        query_vector = [0.49] * VECTOR_DIMENSION
        results = self.store.search(self.workspace_id, query_vector, top_k=2)

        self.assertEqual(len(results), 2)
        # The first result should be chunk_id2 since it is closer to query_vector
        self.assertEqual(results[0].chunk_id, chunk_id2)
        self.assertEqual(results[0].document_id, self.document_id)
        self.assertEqual(results[0].workspace_id, self.workspace_id)
        # Cosine similarity score should be close to 1.0 because they are identical directions
        self.assertAlmostEqual(results[0].score, 1.0, places=4)

    def test_search_empty_index(self):
        self.store.create(self.workspace_id)
        query = [0.1] * VECTOR_DIMENSION
        results = self.store.search(self.workspace_id, query, top_k=5)
        self.assertEqual(results, [])

    def test_dimension_mismatch(self):
        self.store.create(self.workspace_id)
        invalid_vector = [0.1] * 100  # wrong dimension
        metadata = [{"chunk_id": uuid4(), "document_id": self.document_id}]

        with self.assertRaises(DimensionMismatchError):
            self.store.add(self.workspace_id, [invalid_vector], metadata)

        with self.assertRaises(DimensionMismatchError):
            self.store.search(self.workspace_id, invalid_vector)

    def test_delete_document_vectors(self):
        self.store.create(self.workspace_id)

        doc1_id = self.document_id
        doc2_id = uuid4()

        chunk1 = uuid4()
        chunk2 = uuid4()

        vectors = [[0.1] * VECTOR_DIMENSION, [0.2] * VECTOR_DIMENSION]
        metadata = [
            {"chunk_id": chunk1, "document_id": doc1_id},
            {"chunk_id": chunk2, "document_id": doc2_id},
        ]

        self.store.add(self.workspace_id, vectors, metadata)

        # Delete doc1 vectors
        self.store.delete(self.workspace_id, doc1_id)

        # Search again with a query
        query = [0.1] * VECTOR_DIMENSION
        results = self.store.search(self.workspace_id, query, top_k=5)

        # Verify only chunk2 (from doc2) remains
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, chunk2)
        self.assertEqual(results[0].document_id, doc2_id)

    def test_reset_workspace(self):
        self.store.create(self.workspace_id)
        vectors = [[0.1] * VECTOR_DIMENSION]
        metadata = [{"chunk_id": uuid4(), "document_id": self.document_id}]
        
        self.store.add(self.workspace_id, vectors, metadata)
        self.store.reset(self.workspace_id)

        query = [0.1] * VECTOR_DIMENSION
        results = self.store.search(self.workspace_id, query, top_k=5)
        self.assertEqual(results, [])

    @patch("app.services.document_processing_service.PDFParser")
    @patch("app.services.document_processing_service.TextProcessingPipeline")
    @patch("app.embedding.models.SentenceTransformer")
    def test_service_indexing_flow(self, mock_transformer, mock_pipeline, mock_pdf):
        # Setup mocks
        mock_pdf.parse.return_value = MagicMock(text="Parsed text contents", page_count=1)
        mock_pipeline.process.return_value = MagicMock(text="Cleaned text contents", character_count=21, word_count=3)

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * VECTOR_DIMENSION])
        mock_transformer.return_value = mock_model

        # Mock the document stream loader in DocumentService
        with patch("app.services.document_service.DocumentService.get_document_stream") as mock_stream:
            mock_stream.return_value = MagicMock(getvalue=lambda: b"PDF Bytes")

            service = VectorStoreService(self.db)
            stats = service.index_document(self.user_id, self.document_id)

            self.assertIn("chunks", stats)
            self.assertIn("vectors", stats)
            self.assertEqual(stats["dimension"], VECTOR_DIMENSION)

            # Re-index to test clean replacement
            stats_reindex = service.index_document(self.user_id, self.document_id)
            self.assertEqual(stats_reindex["vectors"], stats["vectors"])


if __name__ == "__main__":
    unittest.main()
