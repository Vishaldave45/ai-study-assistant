import unittest
import tempfile
from uuid import uuid4
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.enums import UserStatus, DocumentStatus

from app.rag.service import RAGService
from app.rag.exceptions import WorkspaceNotFound, RAGException
from app.llm.schemas import LLMResponse
from fastapi import HTTPException

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rag_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestRAG(unittest.TestCase):

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

        # Mock LLMService to avoid loading/calling Gemini
        self.llm_patcher = patch("app.rag.pipeline.LLMService")
        self.mock_llm_class = self.llm_patcher.start()
        self.mock_llm_service = self.mock_llm_class.return_value

        # Mock RetrievalService to avoid real vector store search
        self.retrieval_patcher = patch("app.rag.pipeline.RetrievalService")
        self.mock_retrieval_class = self.retrieval_patcher.start()
        self.mock_retrieval_service = self.mock_retrieval_class.return_value

        # Create test owner
        self.user_id = uuid4()
        self.user = User(
            id=self.user_id,
            email=f"rag_user_{uuid4().hex[:6]}@example.com",
            full_name="RAG Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(self.user)

        # Create test workspace
        self.workspace_id = uuid4()
        self.workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Workspace A",
        )
        self.db.add(self.workspace)

        # Create ready document
        self.doc_id = uuid4()
        self.doc = Document(
            id=self.doc_id,
            workspace_id=self.workspace_id,
            original_filename="ai_intro.pdf",
            stored_filename="stored_ai.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.doc)
        self.db.commit()

        # Mock index_exists to True for the workspace so validator passes
        self.patcher_exists = patch(
            "app.vectorstore.faiss_store.FAISSVectorStore.index_exists",
            return_value=True,
        )
        self.patcher_exists.start()

    def tearDown(self):
        self.db.close()
        self.patcher1.stop()
        self.embedding_patcher.stop()
        self.llm_patcher.stop()
        self.retrieval_patcher.stop()
        self.patcher_exists.stop()
        self.temp_dir.cleanup()

    def test_successful_rag_query(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        # 1. Mock retriever to return one relevant chunk
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(self.doc_id),
            text="Neural Networks are inspired by the brain.",
            score=0.92,
            page=0,
            chunk_index=0,
            metadata={"original_filename": "ai_intro.pdf"}
        )
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Explain CNN",
            chunks=[chunk]
        )

        # 2. Mock LLM response
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer="Neural Networks are computational models inspired by the brain.",
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage={"prompt_tokens": 50, "output_tokens": 15},
        )

        service = RAGService(self.db)
        response = service.query(self.workspace_id, "Explain CNN", self.user_id)

        self.assertIn("computational models", response.answer)
        self.assertEqual(len(response.citations), 1)
        self.assertEqual(response.citations[0].document, "ai_intro.pdf")
        self.assertEqual(response.citations[0].score, 0.92)
        self.assertEqual(response.chunks_used, 1)
        self.assertGreaterEqual(response.processing_time_ms, 0)

    def test_empty_question_raises_422(self):
        service = RAGService(self.db)
        with self.assertRaises(HTTPException) as ctx:
            service.query(self.workspace_id, "  ", self.user_id)
        self.assertEqual(ctx.exception.status_code, 422)

    def test_missing_workspace_raises_404(self):
        service = RAGService(self.db)
        with self.assertRaises(WorkspaceNotFound):
            service.query(uuid4(), "Explain AI", self.user_id)

    def test_unauthorized_user_raises_403(self):
        unauthorized_user_id = uuid4()
        service = RAGService(self.db)
        with self.assertRaises(HTTPException) as ctx:
            service.query(self.workspace_id, "Explain AI", unauthorized_user_id)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_no_relevant_chunks_returns_graceful_fallback(self):
        from app.retrieval.models import RetrievalResult
        # Mock retriever to return no relevant chunks
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Explain quantum physics",
            chunks=[]
        )

        service = RAGService(self.db)
        response = service.query(
            self.workspace_id, "Explain quantum physics", self.user_id
        )

        self.assertEqual(
            response.answer,
            "I couldn't find relevant information in your uploaded documents.",
        )
        self.assertEqual(len(response.citations), 0)

    def test_no_indexed_documents_raises_400(self):
        # Create a new workspace with no indexed documents
        empty_workspace_id = uuid4()
        empty_workspace = Workspace(
            id=empty_workspace_id,
            owner_id=self.user_id,
            name="Empty Workspace",
        )
        self.db.add(empty_workspace)
        self.db.commit()

        service = RAGService(self.db)
        with self.assertRaises(RAGException) as ctx:
            service.query(empty_workspace_id, "Explain AI", self.user_id)
        self.assertIn("No indexed documents found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
