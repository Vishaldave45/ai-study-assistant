import unittest
from uuid import uuid4
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

from app.database.enums import ConversationStatus, MessageRole
from app.database.models.conversation import Conversation
from app.database.models.message import Message
from app.database.models.user import User
from app.exceptions.chat import (
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationNotFoundError,
)
from app.llm.schemas import LLMResponse
from app.prompts.builder import PromptBuilder
from app.retrieval.schemas import SearchResponse, SearchResponseItem
from app.schemas.chat import ChatResponse
from app.services.chat.chat_service import ChatService


class TestChatService(unittest.TestCase):

    def setUp(self):
        # Create mock dependencies
        self.mock_conv_service = MagicMock()
        self.mock_message_repo = MagicMock()
        self.mock_citation_repo = MagicMock()
        self.mock_retrieval_service = MagicMock()
        self.mock_prompt_builder = MagicMock()
        self.mock_llm_service = MagicMock()
        self.mock_conv_repo = MagicMock()
        
        # Mock DB session in the repository
        self.mock_db = MagicMock()
        self.mock_message_repo.db = self.mock_db

        self.service = ChatService(
            conversation_service=self.mock_conv_service,
            message_repo=self.mock_message_repo,
            citation_repo=self.mock_citation_repo,
            retrieval_service=self.mock_retrieval_service,
            prompt_builder=self.mock_prompt_builder,
            llm_service=self.mock_llm_service,
            conversation_repo=self.mock_conv_repo,
        )

        # Common test entities
        self.user = User(id=uuid4(), email="user@example.com", full_name="User Test")
        self.conversation = Conversation(
            id=uuid4(),
            workspace_id=uuid4(),
            user_id=self.user.id,
            title="New Chat",
            status=ConversationStatus.ACTIVE,
            last_message_at=datetime.now(UTC),
        )

    def test_chat_success(self):
        # Setup mocks
        self.mock_conv_service.get_conversation.return_value = self.conversation
        self.mock_conv_service.generate_default_title.return_value = "New Chat"

        # Mock user and assistant message creations
        user_msg = Message(id=uuid4(), conversation_id=self.conversation.id, role=MessageRole.USER, content="Explain CNN")
        asst_msg = Message(id=uuid4(), conversation_id=self.conversation.id, role=MessageRole.ASSISTANT, content="CNN stands for...")
        self.mock_message_repo.create.side_effect = [user_msg, asst_msg]

        from app.retrieval.models import RetrievalResult, RetrievedChunk
        # Mock retrieval results
        chunk_id = uuid4()
        doc_id = uuid4()
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Explain CNN",
            chunks=[
                RetrievedChunk(
                    chunk_id=str(chunk_id),
                    document_id=str(doc_id),
                    score=0.95,
                    text="CNN explanation content",
                    page=0,
                    chunk_index=0,
                    metadata={"original_filename": "CNN Document"}
                )
            ]
        )

        # Mock prompt builder
        self.mock_prompt_builder.build_with_history.return_value = ("Compiled Prompt", 1)

        # Mock LLM generation
        self.mock_llm_service.generate.side_effect = [
            LLMResponse(answer="CNN stands for...", usage={"prompt_token_count": 100, "candidates_token_count": 50}, model="gemini-2.5", finish_reason="stop"),
            LLMResponse(answer="CNN Notes", usage=None, model="gemini-2.5", finish_reason="stop")  # For title generation
        ]

        # Call service
        response = self.service.chat(
            conversation_id=self.conversation.id,
            question="Explain CNN",
            current_user=self.user,
        )

        # Assertions
        self.assertIsInstance(response, ChatResponse)
        self.assertEqual(response.answer, "CNN stands for...")
        self.assertEqual(len(response.citations), 1)
        self.assertEqual(response.citations[0].document_id, doc_id)
        self.assertEqual(response.usage.total_tokens, 150)

        # Verify DB calls
        self.assertEqual(self.mock_message_repo.create.call_count, 2)
        self.mock_citation_repo.bulk_create.assert_called_once()
        self.mock_conv_repo.rename.assert_called_once_with(self.conversation, "CNN Notes")
        self.assertEqual(self.mock_db.commit.call_count, 2)  # One for user message, one for assistant response + title

    def test_chat_unauthorized_conversation(self):
        # Mocks
        self.mock_conv_service.get_conversation.side_effect = ConversationAccessDeniedError("Access Denied")

        with self.assertRaises(ConversationAccessDeniedError):
            self.service.chat(
                conversation_id=self.conversation.id,
                question="Explain CNN",
                current_user=self.user,
            )

        self.mock_message_repo.create.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_chat_archived_conversation(self):
        self.mock_conv_service.get_conversation.return_value = self.conversation
        self.mock_conv_service.validate_can_message.side_effect = ConversationArchivedError("Archived")

        with self.assertRaises(ConversationArchivedError):
            self.service.chat(
                conversation_id=self.conversation.id,
                question="Explain CNN",
                current_user=self.user,
            )

        self.mock_message_repo.create.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_chat_llm_failure_retains_user_message(self):
        # Setup mocks
        self.mock_conv_service.get_conversation.return_value = self.conversation
        user_msg = Message(id=uuid4(), conversation_id=self.conversation.id, role=MessageRole.USER, content="Explain CNN")
        self.mock_message_repo.create.return_value = user_msg

        from app.retrieval.models import RetrievalResult
        # Mock retrieval
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(query="Explain CNN", chunks=[])
        self.mock_prompt_builder.build_with_history.return_value = ("Compiled Prompt", 0)

        # Mock LLM generation to throw an error
        self.mock_llm_service.generate.side_effect = Exception("LLM Timeout or API Error")

        with self.assertRaises(Exception):
            self.service.chat(
                conversation_id=self.conversation.id,
                question="Explain CNN",
                current_user=self.user,
            )

        # Verify that the USER message was still created and committed
        self.mock_message_repo.create.assert_called_once_with(
            conversation_id=self.conversation.id,
            role=MessageRole.USER,
            content="Explain CNN",
        )
        self.mock_db.commit.assert_called_once()  # User message committed
        self.mock_db.rollback.assert_not_called()  # Outer block didn't rollback the user msg (since it already committed)

    def test_chat_title_auto_generation_skipped(self):
        # If conversation title is not default, skip rename
        self.conversation.title = "Custom Chat Title"
        self.mock_conv_service.get_conversation.return_value = self.conversation
        self.mock_conv_service.generate_default_title.return_value = "New Chat"

        # Mock messages
        user_msg = Message(id=uuid4(), conversation_id=self.conversation.id, role=MessageRole.USER, content="Explain CNN")
        asst_msg = Message(id=uuid4(), conversation_id=self.conversation.id, role=MessageRole.ASSISTANT, content="CNN stands for...")
        self.mock_message_repo.create.side_effect = [user_msg, asst_msg]

        from app.retrieval.models import RetrievalResult
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(query="Explain CNN", chunks=[])
        self.mock_prompt_builder.build_with_history.return_value = ("Compiled Prompt", 0)

        self.mock_llm_service.generate.return_value = LLMResponse(
            answer="CNN stands for...", usage=None, model="gemini-2.5", finish_reason="stop"
        )

        response = self.service.chat(
            conversation_id=self.conversation.id,
            question="Explain CNN",
            current_user=self.user,
        )

        # Verify rename was NOT called
        self.mock_conv_repo.rename.assert_not_called()


if __name__ == "__main__":
    unittest.main()
