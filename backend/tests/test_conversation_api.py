import unittest
from datetime import datetime, UTC
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.enums import ConversationStatus, UserStatus
from app.database.models.conversation import Conversation
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app

# Create file-based SQLite engine for testing API connections
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override globals
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


class TestConversationAPI(unittest.TestCase):

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
        if os.path.exists("test_api.db"):
            try:
                os.remove("test_api.db")
            except Exception:
                pass

    def setUp(self):
        global current_test_user, current_db_session
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

        # Create workspaces
        self.workspace1 = Workspace(
            id=uuid4(),
            owner_id=self.user1.id,
            name="User 1 Workspace",
        )
        self.workspace2 = Workspace(
            id=uuid4(),
            owner_id=self.user2.id,
            name="User 2 Workspace",
        )
        self.db.add(self.workspace1)
        self.db.add(self.workspace2)
        self.db.commit()

        # Default authenticated user
        current_test_user = self.user1

    def tearDown(self):
        self.db.close()

    def test_create_conversation_success(self):
        payload = {"workspace_id": str(self.workspace1.id)}
        response = self.client.post("/api/v1/conversations", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "New Chat")
        self.assertEqual(data["workspace_id"], str(self.workspace1.id))
        self.assertEqual(data["status"], "ACTIVE")
        self.assertIn("id", data)

    def test_create_conversation_workspace_not_found(self):
        payload = {"workspace_id": str(uuid4())}
        response = self.client.post("/api/v1/conversations", json=payload)
        self.assertEqual(response.status_code, 404)

    def test_create_conversation_workspace_access_denied(self):
        # User 1 tries to create conversation in User 2's workspace
        payload = {"workspace_id": str(self.workspace2.id)}
        response = self.client.post("/api/v1/conversations", json=payload)
        self.assertEqual(response.status_code, 403)

    def test_list_conversations_success(self):
        # Create some conversations
        c1 = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Chat 1",
            status=ConversationStatus.ACTIVE,
        )
        c2 = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Chat 2",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c1)
        self.db.add(c2)
        self.db.commit()

        response = self.client.get(f"/api/v1/conversations?workspace_id={self.workspace1.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["items"]), 2)
        titles = [item["title"] for item in data["items"]]
        self.assertIn("Chat 1", titles)
        self.assertIn("Chat 2", titles)

    def test_list_conversations_workspace_access_denied(self):
        response = self.client.get(f"/api/v1/conversations?workspace_id={self.workspace2.id}")
        self.assertEqual(response.status_code, 403)

    def test_get_conversation_success(self):
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Chat Detail",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        response = self.client.get(f"/api/v1/conversations/{c.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(c.id))
        self.assertEqual(data["title"], "Chat Detail")

    def test_get_conversation_not_found(self):
        response = self.client.get(f"/api/v1/conversations/{uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_get_conversation_access_denied(self):
        global current_test_user
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="User 1 Chat",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        # Log in as User 2
        current_test_user = self.user2
        response = self.client.get(f"/api/v1/conversations/{c.id}")
        self.assertEqual(response.status_code, 403)

    def test_rename_conversation_success(self):
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Original Name",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        payload = {"title": "  New Name  "}
        response = self.client.patch(f"/api/v1/conversations/{c.id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "New Name")

    def test_rename_conversation_validation_error(self):
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Original Name",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        # Validation: empty title
        payload = {"title": ""}
        response = self.client.patch(f"/api/v1/conversations/{c.id}", json=payload)
        self.assertEqual(response.status_code, 422)  # Pydantic validation error is 422 Unprocessable Content

    def test_archive_conversation_success(self):
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Chat to Archive",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        response = self.client.patch(f"/api/v1/conversations/{c.id}/archive")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ARCHIVED")

    def test_delete_conversation_success(self):
        c = Conversation(
            id=uuid4(),
            workspace_id=self.workspace1.id,
            user_id=self.user1.id,
            title="Chat to Delete",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(c)
        self.db.commit()

        response = self.client.delete(f"/api/v1/conversations/{c.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Conversation deleted successfully.")

        # Ensure subsequent get returns 404
        get_response = self.client.get(f"/api/v1/conversations/{c.id}")
        self.assertEqual(get_response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
