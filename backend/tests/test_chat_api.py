import unittest
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.enums import ConversationStatus, UserStatus, MessageRole

from app.database.models.conversation import Conversation
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.llm.schemas import LLMResponse
from app.llm.service import LLMService
from app.main import app
from app.retrieval.schemas import SearchResponse, SearchResponseItem
from app.retrieval.service import RetrievalService

# Create file-based SQLite engine for testing API connections
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_chat_api_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override globals
current_test_user = None
current_db_session = None

# Mock Services
mock_llm_service = MagicMock = None
mock_retrieval_service = MagicMock = None


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


class TestChatAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        # Register FastAPI dependency overrides
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
        import os
        if os.path.exists("test_chat_api_db.db"):
            try:
                os.remove("test_chat_api_db.db")
            except Exception:
                pass

    def setUp(self):
        global current_test_user, current_db_session, mock_llm_service, mock_retrieval_service
        self.db = TestingSessionLocal()
        current_db_session = self.db

        # Create test users
        self.user1 = User(
            id=uuid4(),
            email=f"user1_{uuid4().hex[:6]}@example.com",
            full_name="User One",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.user2 = User(
            id=uuid4(),
            email=f"user2_{uuid4().hex[:6]}@example.com",
            full_name="User Two",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(self.user1)
        self.db.add(self.user2)
        self.db.commit()

        # Create workspace owned by User 1
        self.workspace = Workspace(
            id=uuid4(),
            owner_id=self.user1.id,
            name="User 1 Workspace",
        )
        self.db.add(self.workspace)
        self.db.commit()

        # Create active and archived conversations
        self.active_conv = Conversation(
            id=uuid4(),
            workspace_id=self.workspace.id,
            user_id=self.user1.id,
            title="New Chat",
            status=ConversationStatus.ACTIVE,
        )
        self.archived_conv = Conversation(
            id=uuid4(),
            workspace_id=self.workspace.id,
            user_id=self.user1.id,
            title="Old Chat",
            status=ConversationStatus.ARCHIVED,
        )
        self.db.add(self.active_conv)
        self.db.add(self.archived_conv)
        self.db.commit()

        # Default authenticated user is User 1
        current_test_user = self.user1

        # Setup mock dependencies
        from unittest.mock import MagicMock
        mock_llm_service = MagicMock(spec=LLMService)
        mock_retrieval_service = MagicMock(spec=RetrievalService)

        # We override LLMService and RetrievalService in app.dependency_overrides as well
        # but since ChatService fetches them, we can override get_chat_service directly for simplicity!
        from app.dependencies.chat import get_chat_service
        from app.services.chat.chat_service import ChatService
        from app.services.chat.conversation_service import ConversationService
        from app.repositories.message_repository import MessageRepository
        from app.repositories.message_citation_repository import MessageCitationRepository
        from app.repositories.conversation_repository import ConversationRepository
        from app.repositories.workspace_repository import WorkspaceRepository
        from app.prompts.builder import PromptBuilder


        # Instantiate actual repos but mock services
        conv_service = ConversationService(ConversationRepository(self.db), WorkspaceRepository(self.db))
        chat_service_instance = ChatService(
            conversation_service=conv_service,
            message_repo=MessageRepository(self.db),
            citation_repo=MessageCitationRepository(self.db),
            retrieval_service=mock_retrieval_service,
            prompt_builder=PromptBuilder(),
            llm_service=mock_llm_service,
            conversation_repo=ConversationRepository(self.db),
        )

        app.dependency_overrides[get_chat_service] = lambda: chat_service_instance

        self.mock_llm = mock_llm_service
        self.mock_retrieval = mock_retrieval_service

    def tearDown(self):
        self.db.close()
        # Reset get_chat_service override
        from app.dependencies.chat import get_chat_service
        if get_chat_service in app.dependency_overrides:
            del app.dependency_overrides[get_chat_service]

    def test_chat_api_success(self):
        from app.retrieval.models import RetrievalResult
        # Mock retrieval results
        self.mock_retrieval.retrieve.return_value = RetrievalResult(query="Explain CNN", chunks=[])

        # Mock LLM response
        self.mock_llm.generate.return_value = LLMResponse(
            answer="CNN is a Convolutional Neural Network.",
            usage={"prompt_token_count": 50, "candidates_token_count": 30},
            model="gemini-2.5",
            finish_reason="stop"
        )

        payload = {
            "conversation_id": str(self.active_conv.id),
            "question": "Explain CNN"
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["conversation_id"], str(self.active_conv.id))
        self.assertEqual(data["answer"], "CNN is a Convolutional Neural Network.")
        self.assertEqual(data["usage"]["total_tokens"], 80)
        self.assertIn("message_id", data)

    def test_chat_api_unauthorized_conversation(self):
        global current_test_user
        current_test_user = self.user2  # Logged in as User 2

        payload = {
            "conversation_id": str(self.active_conv.id),
            "question": "Explain CNN"
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 403)

    def test_chat_api_conversation_archived(self):
        payload = {
            "conversation_id": str(self.archived_conv.id),
            "question": "Explain CNN"
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_chat_api_conversation_not_found(self):
        payload = {
            "conversation_id": str(uuid4()),
            "question": "Explain CNN"
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 404)

    def test_chat_api_validation_error(self):
        # Empty question
        payload = {
            "conversation_id": str(self.active_conv.id),
            "question": "   "
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 422)  # Unprocessable Content from Pydantic validator

    def test_chat_api_gemini_failure_retains_user_message(self):
        from app.retrieval.models import RetrievalResult
        # Mock retrieval results
        self.mock_retrieval.retrieve.return_value = RetrievalResult(query="Explain CNN", chunks=[])

        # Mock LLM response to raise exception
        self.mock_llm.generate.side_effect = Exception("LLM Timeout")

        payload = {
            "conversation_id": str(self.active_conv.id),
            "question": "This prompt will fail generation"
        }

        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Failed to generate response")

        # Verify that the USER message was STILL stored in the database!
        from app.database.models.message import Message
        from sqlalchemy import select
        stmt = select(Message).where(
            Message.conversation_id == self.active_conv.id,
            Message.role == MessageRole.USER
        )
        saved_messages = self.db.execute(stmt).scalars().all()
        self.assertEqual(len(saved_messages), 1)
        self.assertEqual(saved_messages[0].content, "This prompt will fail generation")


if __name__ == "__main__":
    unittest.main()
