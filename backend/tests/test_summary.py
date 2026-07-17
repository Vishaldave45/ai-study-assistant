import unittest
import os
from uuid import uuid4
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.enums import UserStatus, DocumentStatus
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app

from app.prompts.summary.builder import SummaryPromptBuilder
from app.prompts.summary.templates import SummaryTemplateType
from app.services.summary.service import SummaryService
from app.schemas.summary.request import SummaryRequest
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
from app.llm.schemas import LLMResponse

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_summary.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency overrides globals
current_test_user = None
current_db_session = None


def override_get_db():
    try:
        yield current_db_session
    finally:
        pass


def override_get_current_user():
    if current_test_user is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return current_test_user


class TestSummary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
        if os.path.exists("test_summary.db"):
            try:
                os.remove("test_summary.db")
            except Exception:
                pass

    def setUp(self):
        global current_test_user, current_db_session
        self.db = TestingSessionLocal()
        current_db_session = self.db

        # Mock LLMService to avoid actual API requests
        self.llm_patcher = patch("app.services.summary.service.LLMService")
        self.mock_llm_class = self.llm_patcher.start()
        self.mock_llm_service = self.mock_llm_class.return_value

        # Create test users
        self.user1_id = uuid4()
        self.user1 = User(
            id=self.user1_id,
            email=f"summary_user1_{uuid4().hex[:6]}@example.com",
            full_name="Summary Owner",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.user2_id = uuid4()
        self.user2 = User(
            id=self.user2_id,
            email=f"summary_user2_{uuid4().hex[:6]}@example.com",
            full_name="Summary Guest",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(self.user1)
        self.db.add(self.user2)
        self.db.commit()

        # Create workspaces
        self.workspace1_id = uuid4()
        self.workspace1 = Workspace(
            id=self.workspace1_id,
            owner_id=self.user1_id,
            name="Workspace One",
        )
        self.workspace2_id = uuid4()
        self.workspace2 = Workspace(
            id=self.workspace2_id,
            owner_id=self.user2_id,
            name="Workspace Two",
        )
        self.db.add(self.workspace1)
        self.db.add(self.workspace2)
        self.db.commit()

        # Create documents for workspace1
        self.doc1_id = uuid4()
        self.doc1 = Document(
            id=self.doc1_id,
            workspace_id=self.workspace1_id,
            original_filename="notes.pdf",
            stored_filename="stored_notes.pdf",
            mime_type="application/pdf",
            file_size=500,
            status=DocumentStatus.READY,
        )
        self.doc2_id = uuid4()
        self.doc2 = Document(
            id=self.doc2_id,
            workspace_id=self.workspace1_id,
            original_filename="draft.pdf",
            stored_filename="stored_draft.pdf",
            mime_type="application/pdf",
            file_size=300,
            status=DocumentStatus.PROCESSING,  # Not ready
        )
        self.db.add(self.doc1)
        self.db.add(self.doc2)
        self.db.commit()

        # Add chunks for doc1
        self.chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=self.doc1_id,
            chunk_index=0,
            content="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python.",
            token_count=20,
            character_count=98,
            start_offset=0,
            end_offset=98,
        )
        self.chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=self.doc1_id,
            chunk_index=1,
            content="It is based on standard Python type hints.",
            token_count=10,
            character_count=41,
            start_offset=99,
            end_offset=140,
        )
        self.db.add(self.chunk1)
        self.db.add(self.chunk2)
        self.db.commit()

        # Set default authenticated user
        current_test_user = self.user1

    def tearDown(self):
        self.llm_patcher.stop()
        self.db.close()

    # =========================================================================
    # 1. Prompt Builder Tests
    # =========================================================================
    def test_prompt_builder_basic(self):
        builder = SummaryPromptBuilder()
        chunks = [
            {"content": "Chunk 1 content", "filename": "test.pdf", "page": "N/A"},
            {"content": "Chunk 2 content", "filename": "test.pdf", "page": "N/A"},
        ]
        prompt, chunk_count = builder.build(chunks, SummaryTemplateType.SHORT)
        self.assertEqual(chunk_count, 2)
        self.assertIn("System Instruction", prompt)
        self.assertIn("Chunk 1 content", prompt)
        self.assertIn("Chunk 2 content", prompt)
        self.assertIn("concise, 1-2 paragraph summary", prompt.lower() or "concise")

    # =========================================================================
    # 2. Service Layer Tests
    # =========================================================================
    def test_service_summary_workspace_wide_success(self):
        # Mock LLM Response
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer="This is a summary of FastAPI.",
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage={"prompt_tokens": 100, "completion_tokens": 10},
        )

        service = SummaryService(self.db)
        request = SummaryRequest(
            workspace_id=self.workspace1_id,
            template_type=SummaryTemplateType.SHORT
        )
        response = service.generate_summary(
            workspace_id=self.workspace1_id,
            current_user_id=self.user1_id,
            request=request
        )

        self.assertEqual(response.summary, "This is a summary of FastAPI.")
        self.assertEqual(response.chunk_count, 2)
        self.assertEqual(response.model, "gemini-2.5-flash")
        self.assertGreaterEqual(response.processing_time_ms, 0)

    def test_service_summary_document_specific_success(self):
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer="Document summary.",
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        service = SummaryService(self.db)
        request = SummaryRequest(
            workspace_id=self.workspace1_id,
            document_id=self.doc1_id,
            template_type=SummaryTemplateType.BULLET
        )
        response = service.generate_summary(
            workspace_id=self.workspace1_id,
            current_user_id=self.user1_id,
            request=request
        )
        self.assertEqual(response.summary, "Document summary.")
        self.assertEqual(response.chunk_count, 2)

    def test_service_summary_workspace_not_found(self):
        service = SummaryService(self.db)
        request = SummaryRequest(workspace_id=uuid4())
        with self.assertRaises(WorkspaceNotFoundError):
            service.generate_summary(
                workspace_id=request.workspace_id,
                current_user_id=self.user1_id,
                request=request
            )

    def test_service_summary_workspace_access_denied(self):
        # user2 tries to access workspace1
        service = SummaryService(self.db)
        request = SummaryRequest(workspace_id=self.workspace1_id)
        with self.assertRaises(WorkspaceAccessDeniedError):
            service.generate_summary(
                workspace_id=self.workspace1_id,
                current_user_id=self.user2_id,
                request=request
            )

    def test_service_summary_document_not_found(self):
        service = SummaryService(self.db)
        request = SummaryRequest(
            workspace_id=self.workspace1_id,
            document_id=uuid4()
        )
        with self.assertRaises(DocumentNotFoundError):
            service.generate_summary(
                workspace_id=self.workspace1_id,
                current_user_id=self.user1_id,
                request=request
            )

    def test_service_summary_document_different_workspace(self):
        # Create a document in workspace2
        doc_w2 = Document(
            id=uuid4(),
            workspace_id=self.workspace2_id,
            original_filename="w2.pdf",
            stored_filename="stored_w2.pdf",
            mime_type="application/pdf",
            file_size=10,
            status=DocumentStatus.READY,
        )
        self.db.add(doc_w2)
        self.db.commit()

        service = SummaryService(self.db)
        request = SummaryRequest(
            workspace_id=self.workspace1_id,
            document_id=doc_w2.id
        )
        with self.assertRaises(DocumentAccessDeniedError):
            service.generate_summary(
                workspace_id=self.workspace1_id,
                current_user_id=self.user1_id,
                request=request
            )

    def test_service_summary_document_not_ready(self):
        service = SummaryService(self.db)
        request = SummaryRequest(
            workspace_id=self.workspace1_id,
            document_id=self.doc2_id
        )
        with self.assertRaises(ValueError) as ctx:
            service.generate_summary(
                workspace_id=self.workspace1_id,
                current_user_id=self.user1_id,
                request=request
            )
        self.assertIn("not ready", str(ctx.exception))

    def test_service_summary_no_ready_documents(self):
        # Create an empty workspace
        w_empty = Workspace(id=uuid4(), owner_id=self.user1_id, name="Empty Workspace")
        self.db.add(w_empty)
        self.db.commit()

        service = SummaryService(self.db)
        request = SummaryRequest(workspace_id=w_empty.id)
        with self.assertRaises(ValueError) as ctx:
            service.generate_summary(
                workspace_id=w_empty.id,
                current_user_id=self.user1_id,
                request=request
            )
        self.assertIn("No indexed or processed documents found", str(ctx.exception))

    # =========================================================================
    # 3. API Integration Tests
    # =========================================================================
    def test_api_generate_summary_success(self):
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer="Awesome API summary.",
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage={"prompt_tokens": 10},
        )

        payload = {
            "workspace_id": str(self.workspace1_id),
            "template_type": "detailed"
        }
        response = self.client.post("/api/v1/summary", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["summary"], "Awesome API summary.")
        self.assertEqual(data["chunk_count"], 2)
        self.assertEqual(data["model"], "gemini-2.5-flash")

    def test_api_generate_summary_workspace_not_found(self):
        payload = {
            "workspace_id": str(uuid4()),
            "template_type": "short"
        }
        response = self.client.post("/api/v1/summary", json=payload)
        self.assertEqual(response.status_code, 404)

    def test_api_generate_summary_unauthorized_guest(self):
        global current_test_user
        # Log in as user2
        current_test_user = self.user2

        payload = {
            "workspace_id": str(self.workspace1_id),
            "template_type": "short"
        }
        response = self.client.post("/api/v1/summary", json=payload)
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
