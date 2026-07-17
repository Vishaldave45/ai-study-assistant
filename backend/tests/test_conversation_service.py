import unittest
from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.enums import ConversationStatus, UserStatus
from app.database.models.conversation import Conversation
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.exceptions.chat import (
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationNotFoundError,
)
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceNotFoundError,
)
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.chat.conversation_service import ConversationService

# Use in-memory SQLite for service testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestConversationService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()
        self.conversation_repo = ConversationRepository(self.db)
        self.workspace_repo = WorkspaceRepository(self.db)
        self.service = ConversationService(
            conversation_repo=self.conversation_repo,
            workspace_repo=self.workspace_repo,
        )

        # Setup standard test users
        self.user1_id = uuid4()
        self.user1 = User(
            id=self.user1_id,
            email=f"user1_{uuid4().hex[:6]}@example.com",
            full_name="User One",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )

        self.user2_id = uuid4()
        self.user2 = User(
            id=self.user2_id,
            email=f"user2_{uuid4().hex[:6]}@example.com",
            full_name="User Two",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )

        self.db.add(self.user1)
        self.db.add(self.user2)
        self.db.commit()

        # Setup workspaces
        self.workspace1 = self.workspace_repo.create(
            owner_id=self.user1_id,
            name="User 1 Workspace",
        )
        self.workspace2 = self.workspace_repo.create(
            owner_id=self.user2_id,
            name="User 2 Workspace",
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_create_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        self.assertEqual(conv.title, "New Chat")
        self.assertEqual(conv.workspace_id, self.workspace1.id)
        self.assertEqual(conv.user_id, self.user1_id)
        self.assertEqual(conv.status, ConversationStatus.ACTIVE)

    def test_create_conversation_workspace_not_found(self):
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.create_conversation(
                workspace_id=uuid4(),
                user_id=self.user1_id,
            )

    def test_create_conversation_workspace_access_denied(self):
        # User 1 tries to create conversation in User 2's workspace
        with self.assertRaises(WorkspaceAccessDeniedError):
            self.service.create_conversation(
                workspace_id=self.workspace2.id,
                user_id=self.user1_id,
            )

    def test_get_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        fetched = self.service.get_conversation(
            user_id=self.user1_id,
            conversation_id=conv.id,
        )
        self.assertEqual(fetched.id, conv.id)

    def test_get_conversation_not_found(self):
        with self.assertRaises(ConversationNotFoundError):
            self.service.get_conversation(
                user_id=self.user1_id,
                conversation_id=uuid4(),
            )

    def test_get_conversation_access_denied(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        # User 2 tries to fetch User 1's conversation
        with self.assertRaises(ConversationAccessDeniedError):
            self.service.get_conversation(
                user_id=self.user2_id,
                conversation_id=conv.id,
            )

    def test_list_conversations_success(self):
        # Create 5 conversations in workspace 1
        for i in range(5):
            self.service.create_conversation(
                workspace_id=self.workspace1.id,
                user_id=self.user1_id,
                title=f"Chat {i}",
            )

        items, total, total_pages = self.service.list_conversations(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
            page=1,
            page_size=3,
        )
        self.assertEqual(total, 5)
        self.assertEqual(total_pages, 2)
        self.assertEqual(len(items), 3)

    def test_list_conversations_workspace_not_found(self):
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.list_conversations(
                workspace_id=uuid4(),
                user_id=self.user1_id,
            )

    def test_list_conversations_workspace_access_denied(self):
        with self.assertRaises(WorkspaceAccessDeniedError):
            self.service.list_conversations(
                workspace_id=self.workspace2.id,
                user_id=self.user1_id,
            )

    def test_rename_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        renamed = self.service.rename_conversation(
            user_id=self.user1_id,
            conversation_id=conv.id,
            new_title="  Updated Chat Name  ",
        )
        self.assertEqual(renamed.title, "Updated Chat Name")

    def test_rename_conversation_invalid_title(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        # Empty title
        with self.assertRaises(ValueError):
            self.service.rename_conversation(
                user_id=self.user1_id,
                conversation_id=conv.id,
                new_title="",
            )
        # Whitespace title
        with self.assertRaises(ValueError):
            self.service.rename_conversation(
                user_id=self.user1_id,
                conversation_id=conv.id,
                new_title="   ",
            )
        # Too long title (>255)
        with self.assertRaises(ValueError):
            self.service.rename_conversation(
                user_id=self.user1_id,
                conversation_id=conv.id,
                new_title="a" * 256,
            )

    def test_archive_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        archived = self.service.archive_conversation(
            user_id=self.user1_id,
            conversation_id=conv.id,
        )
        self.assertEqual(archived.status, ConversationStatus.ARCHIVED)

        # Test archived validation rule
        with self.assertRaises(ConversationArchivedError):
            self.service.validate_can_message(archived)

    def test_delete_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        self.service.delete_conversation(
            user_id=self.user1_id,
            conversation_id=conv.id,
        )

        # Retrieve should fail with NotFound (as it is soft-deleted)
        with self.assertRaises(ConversationNotFoundError):
            self.service.get_conversation(
                user_id=self.user1_id,
                conversation_id=conv.id,
            )

    def test_touch_conversation_success(self):
        conv = self.service.create_conversation(
            workspace_id=self.workspace1.id,
            user_id=self.user1_id,
        )
        original_time = conv.last_message_at

        # Touch to update timestamp
        timestamp = datetime(2026, 8, 1, 12, 0, 0)
        touched = self.service.touch_conversation(
            conversation_id=conv.id,
            timestamp=timestamp,
        )
        self.assertNotEqual(touched.last_message_at, original_time)
        self.assertEqual(touched.last_message_at.replace(tzinfo=None), timestamp)



if __name__ == "__main__":
    unittest.main()
