import unittest
import os
import json
from uuid import uuid4
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.enums import UserStatus, DocumentStatus
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app

from app.prompts.explain.builder import ExplainPromptBuilder
from app.prompts.explain.templates import ExplainLevel
from app.services.explain.service import ExplainService
from app.schemas.explain.request import ExplainRequest
from app.exceptions.workspace import WorkspaceNotFoundError, WorkspaceAccessDeniedError
from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
from app.llm.schemas import LLMResponse

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_explain.db"
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


class TestExplain(unittest.TestCase):

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
        if os.path.exists("test_explain.db"):
            try:
                os.remove("test_explain.db")
            except Exception:
                pass

    def setUp(self):
        global current_test_user, current_db_session
        self.db = TestingSessionLocal()
        current_db_session = self.db

        # Mock LLMService
        self.llm_patcher = patch("app.services.explain.service.LLMService")
        self.mock_llm_class = self.llm_patcher.start()
        self.mock_llm_service = self.mock_llm_class.return_value

        # Mock RetrievalService
        self.retrieval_patcher = patch("app.services.explain.service.RetrievalService")
        self.mock_retrieval_class = self.retrieval_patcher.start()
        self.mock_retrieval_service = self.mock_retrieval_class.return_value

        # Create test users
        self.user1_id = uuid4()
        self.user1 = User(
            id=self.user1_id,
            email=f"explain_user1_{uuid4().hex[:6]}@example.com",
            full_name="Explain Owner",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.user2_id = uuid4()
        self.user2 = User(
            id=self.user2_id,
            email=f"explain_user2_{uuid4().hex[:6]}@example.com",
            full_name="Explain Guest",
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

        # Create documents
        self.doc1_id = uuid4()
        self.doc1 = Document(
            id=self.doc1_id,
            workspace_id=self.workspace1_id,
            original_filename="manual.pdf",
            stored_filename="stored_manual.pdf",
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

        current_test_user = self.user1

    def tearDown(self):
        self.llm_patcher.stop()
        self.retrieval_patcher.stop()
        self.db.close()

    # =========================================================================
    # 1. Prompt Builder Tests
    # =========================================================================
    def test_prompt_builder_basic(self):
        builder = ExplainPromptBuilder()
        chunks = [
            {"content": "SQL is structured query language.", "filename": "db.pdf"},
        ]
        prompt, chunk_count = builder.build("SQL", chunks, ExplainLevel.BEGINNER)
        self.assertEqual(chunk_count, 1)
        self.assertIn("System Instruction", prompt)
        self.assertIn("SQL is structured query language.", prompt)
        self.assertIn("BEGINNER", prompt)
        self.assertIn("JSON RESPONSE SCHEMA", prompt)

    # =========================================================================
    # 2. Service Layer Tests
    # =========================================================================
    def test_service_explain_success(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        # Mock retriever to return one chunk
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(self.doc1_id),
            text="SQL is structured query language.",
            score=0.9,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "manual.pdf"}
        )
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="SQL",
            chunks=[chunk]
        )

        # Mock LLM Response with clean JSON
        raw_json_response = {
            "explanation": "SQL stands for Structured Query Language.",
            "examples": ["SELECT * FROM users;"],
            "important_points": ["Used for databases", "Declarative"],
            "references": ["manual.pdf (Page 1)"],
            "follow_up_questions": ["What is a JOIN?"]
        }
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer=json.dumps(raw_json_response),
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        service = ExplainService(self.db)
        request = ExplainRequest(
            workspace_id=self.workspace1_id,
            concept="SQL",
            level=ExplainLevel.INTERMEDIATE
        )
        response = service.explain_concept(
            workspace_id=self.workspace1_id,
            current_user_id=self.user1_id,
            request=request
        )

        self.assertEqual(response.explanation, "SQL stands for Structured Query Language.")
        self.assertEqual(len(response.examples), 1)
        self.assertEqual(response.examples[0], "SELECT * FROM users;")
        self.assertEqual(response.model, "gemini-2.5-flash")

    def test_service_explain_document_filtering(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        # Create a second ready document in workspace1
        other_doc_id = uuid4()
        other_doc = Document(
            id=other_doc_id,
            workspace_id=self.workspace1_id,
            original_filename="other.pdf",
            stored_filename="stored_other.pdf",
            mime_type="application/pdf",
            file_size=10,
            status=DocumentStatus.READY,
        )
        self.db.add(other_doc)
        self.db.commit()

        # Mock retriever returning chunks from both docs
        chunk1 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(self.doc1_id),
            text="Doc 1 explanation.",
            score=0.9,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "manual.pdf"}
        )
        chunk2 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(other_doc_id),
            text="Doc 2 explanation.",
            score=0.9,
            page=2,
            chunk_index=0,
            metadata={"original_filename": "other.pdf"}
        )
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Concept",
            chunks=[chunk1, chunk2]
        )

        # Mock LLM response
        raw_json_response = {
            "explanation": "Filtered doc explanation.",
            "examples": [],
            "important_points": [],
            "references": [],
            "follow_up_questions": []
        }
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer=json.dumps(raw_json_response),
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        # Query explaining concept filtered specifically to doc1_id
        service = ExplainService(self.db)
        request = ExplainRequest(
            workspace_id=self.workspace1_id,
            concept="Concept",
            document_id=self.doc1_id,
            level=ExplainLevel.BEGINNER
        )
        
        # We capture the call arguments to prompt builder to verify filtering was applied
        with patch.object(service.prompt_builder, "build", return_value=("mock prompt", 1)) as mock_build:
            response = service.explain_concept(
                workspace_id=self.workspace1_id,
                current_user_id=self.user1_id,
                request=request
            )
            # Verify only chunk1 (from doc1_id) was sent to prompt builder
            called_chunks = mock_build.call_args[1]["chunks"]
            self.assertEqual(len(called_chunks), 1)
            self.assertEqual(called_chunks[0]["filename"], "manual.pdf")

    def test_service_explain_json_markdown_cleaning(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="clean", chunks=[
                RetrievedChunk(
                    chunk_id=str(uuid4()), document_id=str(self.doc1_id), text="...", score=0.9, page=1, chunk_index=0,
                    metadata={"original_filename": "manual.pdf"}
                )
            ]
        )

        # LLM response is wrapped in markdown json block
        wrapped_response = "```json\n{\n  \"explanation\": \"Markdown wrapped JSON works.\"\n}\n```"
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer=wrapped_response,
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        service = ExplainService(self.db)
        request = ExplainRequest(workspace_id=self.workspace1_id, concept="clean")
        response = service.explain_concept(self.workspace1_id, self.user1_id, request)
        self.assertEqual(response.explanation, "Markdown wrapped JSON works.")

    def test_service_explain_malformed_json_fallback(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="fallback", chunks=[
                RetrievedChunk(
                    chunk_id=str(uuid4()), document_id=str(self.doc1_id), text="...", score=0.9, page=1, chunk_index=0,
                    metadata={"original_filename": "manual.pdf"}
                )
            ]
        )

        # Corrupted JSON response
        corrupted_response = "{ explanation: raw text without proper quotes "
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer=corrupted_response,
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        service = ExplainService(self.db)
        request = ExplainRequest(workspace_id=self.workspace1_id, concept="fallback")
        response = service.explain_concept(self.workspace1_id, self.user1_id, request)
        
        # Verify fallback correctly maps raw text to the explanation field
        self.assertEqual(response.explanation, corrupted_response)
        self.assertEqual(response.examples, [])

    def test_service_explain_no_ready_documents(self):
        # Create an empty workspace
        w_empty = Workspace(id=uuid4(), owner_id=self.user1_id, name="Empty Workspace")
        self.db.add(w_empty)
        self.db.commit()

        service = ExplainService(self.db)
        request = ExplainRequest(workspace_id=w_empty.id, concept="SQL")
        with self.assertRaises(ValueError) as ctx:
            service.explain_concept(w_empty.id, self.user1_id, request)
        self.assertIn("No indexed or processed documents", str(ctx.exception))

    # =========================================================================
    # 3. API Integration Tests
    # =========================================================================
    def test_api_explain_concept_success(self):
        from app.retrieval.models import RetrievalResult, RetrievedChunk
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="API", chunks=[
                RetrievedChunk(
                    chunk_id=str(uuid4()), document_id=str(self.doc1_id), text="...", score=0.9, page=1, chunk_index=0,
                    metadata={"original_filename": "manual.pdf"}
                )
            ]
        )

        raw_json_response = {
            "explanation": "API stands for Application Programming Interface.",
            "examples": ["REST APIs", "GraphQL"],
            "important_points": [],
            "references": [],
            "follow_up_questions": []
        }
        self.mock_llm_service.generate.return_value = LLMResponse(
            answer=json.dumps(raw_json_response),
            model="gemini-2.5-flash",
            finish_reason="STOP",
            usage=None,
        )

        payload = {
            "workspace_id": str(self.workspace1_id),
            "concept": "API",
            "level": "analogy"
        }
        response = self.client.post("/api/v1/explain", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["explanation"], "API stands for Application Programming Interface.")
        self.assertEqual(len(data["examples"]), 2)
        self.assertEqual(data["model"], "gemini-2.5-flash")

    def test_api_explain_unauthorized_guest(self):
        global current_test_user
        current_test_user = self.user2

        payload = {
            "workspace_id": str(self.workspace1_id),
            "concept": "API"
        }
        response = self.client.post("/api/v1/explain", json=payload)
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
