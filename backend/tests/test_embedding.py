import unittest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.enums import UserStatus, DocumentStatus
from app.embedding.pipeline import EmbeddingPipeline
from app.embedding.exceptions import EmbeddingModelError, EmbeddingGenerationError
from app.embedding.models import SentenceTransformerProvider

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_embedding_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class TestEmbeddingService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()

        # Create dummy user, workspace, and document
        self.user_id = uuid4()
        user = User(
            id=self.user_id,
            email=f"embed_user_{uuid4().hex[:6]}@example.com",
            full_name="Embed Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(user)

        self.workspace_id = uuid4()
        workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Embed Workspace",
        )
        self.db.add(workspace)

        self.document_id = uuid4()
        self.document = Document(
            id=self.document_id,
            workspace_id=self.workspace_id,
            original_filename="embed_test.pdf",
            stored_filename="stored_embed_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.document)

        # Add some chunks for this document
        self.chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=self.document_id,
            chunk_index=0,
            content="Chunk one text.",
            token_count=4,
            character_count=15,
            start_offset=0,
            end_offset=15,
        )
        self.chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=self.document_id,
            chunk_index=1,
            content="Chunk two text.",
            token_count=4,
            character_count=15,
            start_offset=16,
            end_offset=31,
        )
        self.db.add(self.chunk1)
        self.db.add(self.chunk2)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    @patch("app.embedding.models.SentenceTransformer")
    def test_provider_initialization_failure(self, mock_transformer):
        mock_transformer.side_effect = Exception("Model load failed")
        with self.assertRaises(EmbeddingModelError):
            SentenceTransformerProvider()

    @patch("app.embedding.models.SentenceTransformer")
    def test_embedding_generation_failure(self, mock_transformer):
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        mock_transformer.return_value = mock_model

        provider = SentenceTransformerProvider()
        with self.assertRaises(EmbeddingGenerationError):
            provider.embed("test")

    @patch("app.embedding.models.SentenceTransformer")
    def test_embedding_pipeline_success(self, mock_transformer):
        # Mock SentenceTransformer encoding output
        mock_model = MagicMock()
        import numpy as np
        # BAAI/bge-small-en-v1.5 returns 384 dim vectors
        dummy_vector = np.random.randn(384)
        mock_model.encode.return_value = np.array([dummy_vector, dummy_vector])
        mock_transformer.return_value = mock_model

        # Run pipeline
        pipeline = EmbeddingPipeline(self.db)
        results = pipeline.run_pipeline(self.user_id, self.document_id)

        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0].vector), 384)
        self.assertEqual(results[0].dimension, 384)
        self.assertEqual(results[0].model, "BAAI/bge-small-en-v1.5")

        # Verify document status updated to EMBEDDED
        self.db.refresh(self.document)
        self.assertEqual(self.document.status, DocumentStatus.EMBEDDED)


if __name__ == "__main__":
    unittest.main()
