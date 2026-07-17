import unittest
import tempfile
from pathlib import Path
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

from app.vectorstore.faiss_store import FAISSVectorStore
from app.retrieval.service import RetrievalService
from app.retrieval.config import MIN_SCORE, TOP_K

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_retrieval_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestRetrieval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()

        # Temporary vector storage path
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patcher1 = patch(
            "app.vectorstore.faiss_store.STORAGE_DIR", self.temp_dir.name
        )
        self.patcher1.start()

        # Mock EmbeddingService to avoid loading SentenceTransformer
        self.embedding_patcher = patch("app.retrieval.service.EmbeddingService")
        self.mock_embedding_class = self.embedding_patcher.start()
        self.mock_embedding_service = self.mock_embedding_class.return_value

        # Workspace A
        self.user_id = uuid4()
        user = User(
            id=self.user_id,
            email=f"ret_user_{uuid4().hex[:6]}@example.com",
            full_name="Ret Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(user)

        self.workspace_a_id = uuid4()
        workspace_a = Workspace(
            id=self.workspace_a_id,
            owner_id=self.user_id,
            name="Workspace A",
        )
        self.db.add(workspace_a)

        self.doc_a_id = uuid4()
        self.doc_a = Document(
            id=self.doc_a_id,
            workspace_id=self.workspace_a_id,
            original_filename="doc_a.pdf",
            stored_filename="stored_doc_a.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.doc_a)

        # Chunks for Workspace A
        self.chunk_a1_id = uuid4()
        self.chunk_a1 = DocumentChunk(
            id=self.chunk_a1_id,
            document_id=self.doc_a_id,
            chunk_index=0,
            content="Neural networks are inspired by the biological brain.",
            token_count=10,
            character_count=52,
            start_offset=0,
            end_offset=52,
        )
        self.chunk_a2_id = uuid4()
        self.chunk_a2 = DocumentChunk(
            id=self.chunk_a2_id,
            document_id=self.doc_a_id,
            chunk_index=1,
            content="Fast Fourier Transform is an efficient algorithm to compute DFT.",
            token_count=10,
            character_count=64,
            start_offset=53,
            end_offset=117,
        )
        self.db.add(self.chunk_a1)
        self.db.add(self.chunk_a2)

        # Workspace B (for isolation testing)
        self.workspace_b_id = uuid4()
        workspace_b = Workspace(
            id=self.workspace_b_id,
            owner_id=self.user_id,
            name="Workspace B",
        )
        self.db.add(workspace_b)

        self.doc_b_id = uuid4()
        self.doc_b = Document(
            id=self.doc_b_id,
            workspace_id=self.workspace_b_id,
            original_filename="doc_b.pdf",
            stored_filename="stored_doc_b.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.doc_b)

        self.chunk_b_id = uuid4()
        self.chunk_b = DocumentChunk(
            id=self.chunk_b_id,
            document_id=self.doc_b_id,
            chunk_index=0,
            content="Neural networks can also process images and audio.",
            token_count=10,
            character_count=50,
            start_offset=0,
            end_offset=50,
        )
        self.db.add(self.chunk_b)
        self.db.commit()

        # Seed vector store for Workspace A
        self.store = FAISSVectorStore()
        self.store.create(self.workspace_a_id)

        vec_a1 = [0.0] * 384
        vec_a1[0] = 1.0
        vec_a2 = [0.0] * 384
        vec_a2[1] = 1.0

        self.store.add(
            self.workspace_a_id,
            [vec_a1, vec_a2],
            [
                {"chunk_id": self.chunk_a1_id, "document_id": self.doc_a_id},
                {"chunk_id": self.chunk_a2_id, "document_id": self.doc_a_id},
            ],
        )
        self.store.save(self.workspace_a_id)

        # Seed vector store for Workspace B
        self.store.create(self.workspace_b_id)
        vec_b = [0.0] * 384
        vec_b[0] = 0.95  # close to vec_a1 but isolated

        self.store.add(
            self.workspace_b_id,
            [vec_b],
            [{"chunk_id": self.chunk_b_id, "document_id": self.doc_b_id}],
        )
        self.store.save(self.workspace_b_id)

    def tearDown(self):
        self.db.close()
        self.patcher1.stop()
        self.embedding_patcher.stop()
        self.temp_dir.cleanup()

    def test_successful_retrieval(self):
        # Query close to A1: [0.99, 0.01, ...]
        query_vec = [0.0] * 384
        query_vec[0] = 0.99
        query_vec[1] = 0.01

        mock_emb = MagicMock()
        mock_emb.vector = query_vec
        self.mock_embedding_service.generate_embeddings.return_value = [mock_emb]

        service = RetrievalService(self.db)
        response = service.retrieve(
            workspace_id=self.workspace_a_id,
            query="Neural networks",
            min_score=0.0,
        )

        self.assertEqual(response.query, "Neural networks")
        self.assertEqual(len(response.chunks), 2)

        # Verify ranking order: chunk_a1 is closer (first index 1.0 vs query 0.99)
        self.assertEqual(response.chunks[0].chunk_id, str(self.chunk_a1_id))
        self.assertEqual(response.chunks[0].text, self.chunk_a1.content)

        self.assertEqual(response.chunks[1].chunk_id, str(self.chunk_a2_id))
        self.assertEqual(response.chunks[1].text, self.chunk_a2.content)

    def test_score_threshold_filtering_decoupled(self):
        # In Sprint 1, core semantic retrieval returns all matches without filtering
        query_vec = [0.0] * 384
        query_vec[0] = 1.0

        mock_emb = MagicMock()
        mock_emb.vector = query_vec
        self.mock_embedding_service.generate_embeddings.return_value = [mock_emb]

        service = RetrievalService(self.db)

        response = service.retrieve(
            workspace_id=self.workspace_a_id,
            query="Neural networks",
            min_score=0.0,
        )

        self.assertEqual(len(response.chunks), 2)

    def test_workspace_isolation(self):
        # Query close to A1/B
        query_vec = [0.0] * 384
        query_vec[0] = 1.0

        mock_emb = MagicMock()
        mock_emb.vector = query_vec
        self.mock_embedding_service.generate_embeddings.return_value = [mock_emb]

        service = RetrievalService(self.db)

        # Search Workspace A
        response_a = service.retrieve(
            workspace_id=self.workspace_a_id,
            query="Neural networks",
        )
        # Should not contain chunk_b
        chunk_ids_a = [r.chunk_id for r in response_a.chunks]
        self.assertIn(str(self.chunk_a1_id), chunk_ids_a)
        self.assertNotIn(str(self.chunk_b_id), chunk_ids_a)

        # Search Workspace B
        response_b = service.retrieve(
            workspace_id=self.workspace_b_id,
            query="Neural networks",
        )
        # Should contain chunk_b, and not A1
        chunk_ids_b = [r.chunk_id for r in response_b.chunks]
        self.assertIn(str(self.chunk_b_id), chunk_ids_b)
        self.assertNotIn(str(self.chunk_a1_id), chunk_ids_b)

    def test_empty_workspace_index(self):
        query_vec = [0.0] * 384
        mock_emb = MagicMock()
        mock_emb.vector = query_vec
        self.mock_embedding_service.generate_embeddings.return_value = [mock_emb]

        # Workspace with no index
        empty_workspace_id = uuid4()
        service = RetrievalService(self.db)

        response = service.retrieve(
            workspace_id=empty_workspace_id,
            query="test query",
        )
        self.assertEqual(response.chunks, [])


if __name__ == "__main__":
    unittest.main()
