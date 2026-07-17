import unittest
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.enums import ConversationStatus, DocumentStatus, MessageRole, UserStatus
from app.database.models.conversation import Conversation
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.models.message import Message
from app.database.models.message_citation import MessageCitation
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.repositories.conversation_document_repository import ConversationDocumentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_citation_repository import MessageCitationRepository
from app.repositories.message_repository import MessageRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_repositories.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestRepositoryLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()
        
        # Repositories
        self.conversation_repo = ConversationRepository(self.db)
        self.message_repo = MessageRepository(self.db)
        self.citation_repo = MessageCitationRepository(self.db)
        self.conv_doc_repo = ConversationDocumentRepository(self.db)

        # Setup test parent entities
        self.user_id = uuid4()
        self.user = User(
            id=self.user_id,
            email=f"test_user_{uuid4().hex[:6]}@example.com",
            full_name="Test User",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(self.user)

        self.workspace_id = uuid4()
        self.workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Test Workspace",
        )
        self.db.add(self.workspace)

        self.document_id = uuid4()
        self.document = Document(
            id=self.document_id,
            workspace_id=self.workspace_id,
            original_filename="ai_ethics.pdf",
            stored_filename="stored_ethics.pdf",
            mime_type="application/pdf",
            file_size=5000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.document)

        self.chunk_id = uuid4()
        self.chunk = DocumentChunk(
            id=self.chunk_id,
            document_id=self.document_id,
            chunk_index=0,
            content="AI ethics is a set of values, principles, and techniques...",
            token_count=10,
            character_count=50,
            start_offset=0,
            end_offset=50,
        )
        self.db.add(self.chunk)
        
        self.db.commit()

    def tearDown(self):
        self.db.close()

    # --- ConversationRepository Tests ---

    def test_conversation_crud_and_methods(self):
        # 1. Create
        conv = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Ethics Chat",
            status=ConversationStatus.ACTIVE,
            langgraph_thread_id=uuid4(),
        )
        self.assertIsNotNone(conv.id)
        self.assertEqual(conv.title, "Ethics Chat")
        self.assertEqual(conv.status, ConversationStatus.ACTIVE)

        # 2. Get by ID
        fetched = self.conversation_repo.get_by_id(conv.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Ethics Chat")

        # 3. Exists
        self.assertTrue(self.conversation_repo.exists(conv.id))

        # 4. Rename
        renamed = self.conversation_repo.rename(conv, "Ethics Discussion")
        self.assertEqual(renamed.title, "Ethics Discussion")
        
        # Verify in DB
        self.db.commit()
        self.assertEqual(self.conversation_repo.get_by_id(conv.id).title, "Ethics Discussion")

        # 5. Get thread ID
        thread_id = self.conversation_repo.get_thread_id(conv.id)
        self.assertEqual(thread_id, conv.langgraph_thread_id)

        # 6. Update last message
        old_time = conv.last_message_at
        new_time = datetime.now(UTC) + timedelta(minutes=5)
        self.conversation_repo.update_last_message(conv, new_time)
        self.assertEqual(conv.last_message_at.replace(tzinfo=None), new_time.replace(tzinfo=None))

        # 7. Delete (Soft delete)
        self.conversation_repo.delete(conv)
        self.assertFalse(self.conversation_repo.exists(conv.id))
        self.assertIsNone(self.conversation_repo.get_by_id(conv.id))

    def test_conversation_list_and_sorting(self):
        # Create multiple conversations
        conv1 = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Chat 1",
        )
        conv2 = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Chat 2",
        )

        # Update last_message_at to establish specific order
        now = datetime.now(UTC)
        self.conversation_repo.update_last_message(conv1, now - timedelta(hours=1))
        self.conversation_repo.update_last_message(conv2, now)

        self.db.commit()

        # List by workspace
        workspace_list = self.conversation_repo.list_by_workspace(self.workspace_id)
        self.assertEqual(len(workspace_list), 2)
        # Should be sorted by last_message_at DESC (conv2 first, then conv1)
        self.assertEqual(workspace_list[0].id, conv2.id)
        self.assertEqual(workspace_list[1].id, conv1.id)

        # List by user
        user_list = self.conversation_repo.list_by_user(self.user_id)
        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].id, conv2.id)

    # --- MessageRepository Tests ---

    def test_message_crud(self):
        conv = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Message Test Chat",
        )

        # 1. Create Message
        msg = self.message_repo.create(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Hello AI!",
        )
        msg.created_at = datetime.now(UTC) - timedelta(seconds=10)
        self.db.commit()
        self.assertIsNotNone(msg.id)
        self.assertEqual(msg.content, "Hello AI!")

        # 2. Get Message
        fetched = self.message_repo.get(msg.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.content, "Hello AI!")

        # 3. Create Many
        msg1 = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content="Hello Human!",
            created_at=datetime.now(UTC) - timedelta(seconds=5),
        )
        msg2 = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="How are you?",
            created_at=datetime.now(UTC),
        )
        self.message_repo.create_many([msg1, msg2])

        # 4. Count and List
        count = self.message_repo.count(conv.id)
        self.assertEqual(count, 3)

        list_messages = self.message_repo.list_by_conversation(conv.id)
        self.assertEqual(len(list_messages), 3)
        # Check chronological order (USER -> ASSISTANT -> USER)
        self.assertEqual(list_messages[0].role, MessageRole.USER)
        self.assertEqual(list_messages[1].role, MessageRole.ASSISTANT)
        self.assertEqual(list_messages[2].role, MessageRole.USER)

        # 5. Last Messages (newest first, limit)
        last_messages = self.message_repo.last_messages(conv.id, limit=2)
        self.assertEqual(len(last_messages), 2)
        self.assertEqual(last_messages[0].content, "How are you?")
        self.assertEqual(last_messages[1].content, "Hello Human!")

        # 6. Delete
        self.message_repo.delete(msg)
        self.assertIsNone(self.message_repo.get(msg.id))

    # --- MessageCitationRepository Tests ---

    def test_citation_bulk_create_and_operations(self):
        conv = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Citation Chat",
        )
        msg = self.message_repo.create(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content="This is based on the document.",
        )

        # 1. Bulk Create Citations
        cit1 = MessageCitation(message_id=msg.id, document_chunk_id=self.chunk_id)
        self.citation_repo.bulk_create([cit1])

        # 2. List by Message
        citations = self.citation_repo.list_by_message(msg.id)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0].document_chunk_id, self.chunk_id)
        # Verify selectinload works
        self.assertEqual(citations[0].document_chunk.content, self.chunk.content)

        # 3. Delete by Message
        self.citation_repo.delete_by_message(msg.id)
        self.assertEqual(len(self.citation_repo.list_by_message(msg.id)), 0)

    # --- ConversationDocumentRepository Tests ---

    def test_conversation_document_operations(self):
        conv = self.conversation_repo.create(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            title="Doc Association Chat",
        )

        # 1. Attach Document
        self.conv_doc_repo.attach_document(
            conversation_id=conv.id,
            document_id=self.document_id,
        )

        # 2. Exists
        self.assertTrue(self.conv_doc_repo.exists(conv.id, self.document_id))

        # 3. List Documents
        docs = self.conv_doc_repo.list_documents(conv.id)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].id, self.document_id)

        # 4. Detach Document
        self.conv_doc_repo.detach_document(conv.id, self.document_id)
        self.assertFalse(self.conv_doc_repo.exists(conv.id, self.document_id))
        self.assertEqual(len(self.conv_doc_repo.list_documents(conv.id)), 0)


if __name__ == "__main__":
    unittest.main()
