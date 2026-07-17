import unittest
from datetime import datetime, UTC
from uuid import UUID, uuid4

from pydantic import ValidationError

from app.database.enums import ConversationStatus, MessageRole
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.models.message_citation import MessageCitation
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationSummaryResponse,
    CreateConversationRequest,
    MessageListResponse,
    MessageResponse,
    RenameConversationRequest,
    TokenUsageResponse,
)


class TestChatSchemas(unittest.TestCase):

    def test_create_conversation_request(self):
        ws_id = uuid4()
        req = CreateConversationRequest(workspace_id=ws_id)
        self.assertEqual(req.workspace_id, ws_id)

    def test_rename_conversation_request_validation(self):
        # Valid title (with whitespace that should be trimmed)
        req = RenameConversationRequest(title="  Machine Learning Revision  ")
        self.assertEqual(req.title, "Machine Learning Revision")

        # Invalid title: too long (>255)
        with self.assertRaises(ValidationError):
            RenameConversationRequest(title="a" * 256)

        # Invalid title: empty
        with self.assertRaises(ValidationError):
            RenameConversationRequest(title="")

        # Invalid title: whitespace only
        with self.assertRaises(ValidationError):
            RenameConversationRequest(title="   ")

    def test_chat_request_validation(self):
        conv_id = uuid4()
        # Valid question (with whitespace that should be trimmed)
        req = ChatRequest(conversation_id=conv_id, question="  What is CNN?  ")
        self.assertEqual(req.conversation_id, conv_id)
        self.assertEqual(req.question, "What is CNN?")

        # Invalid question: too long (>5000)
        with self.assertRaises(ValidationError):
            ChatRequest(conversation_id=conv_id, question="a" * 5001)

        # Invalid question: empty
        with self.assertRaises(ValidationError):
            ChatRequest(conversation_id=conv_id, question="")

        # Invalid question: whitespace only
        with self.assertRaises(ValidationError):
            ChatRequest(conversation_id=conv_id, question="    ")

    def test_conversation_response(self):
        cid = uuid4()
        wid = uuid4()
        now = datetime.now(UTC)
        resp = ConversationResponse(
            id=cid,
            workspace_id=wid,
            title="Introduction to AI",
            status=ConversationStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            last_message_at=now,
        )
        self.assertEqual(resp.id, cid)
        self.assertEqual(resp.title, "Introduction to AI")

    def test_citation_response(self):
        doc_id = uuid4()
        resp = CitationResponse(
            document_id=doc_id,
            document_name="ml_notes.pdf",
            page="3",
            score=0.9234,
        )
        self.assertEqual(resp.document_id, doc_id)
        self.assertEqual(resp.document_name, "ml_notes.pdf")
        self.assertEqual(resp.page, "3")
        self.assertEqual(resp.score, 0.9234)

    def test_message_response(self):
        msg_id = uuid4()
        doc_id = uuid4()
        now = datetime.now(UTC)
        resp = MessageResponse(
            id=msg_id,
            role=MessageRole.ASSISTANT,
            content="CNN stands for Convolutional Neural Network.",
            created_at=now,
            citations=[
                CitationResponse(
                    document_id=doc_id,
                    document_name="ml_notes.pdf",
                    page="3",
                    score=0.9234,
                )
            ],
        )
        self.assertEqual(resp.id, msg_id)
        self.assertEqual(resp.citations[0].document_name, "ml_notes.pdf")

    def test_chat_response(self):
        conv_id = uuid4()
        msg_id = uuid4()
        doc_id = uuid4()
        resp = ChatResponse(
            conversation_id=conv_id,
            message_id=msg_id,
            answer="Answer content",
            citations=[
                CitationResponse(
                    document_id=doc_id,
                    document_name="ml_notes.pdf",
                    page="3",
                    score=0.9234,
                )
            ],
            usage=TokenUsageResponse(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
            ),
        )
        self.assertEqual(resp.conversation_id, conv_id)
        self.assertEqual(resp.usage.total_tokens, 150)

    def test_message_citation_orm_properties_mapping(self):
        # Create mock/dummy objects for relationship targets in memory
        doc = Document(original_filename="notes.pdf")
        chunk = DocumentChunk(
            document=doc,
            chunk_index=0,
            token_count=10,
            character_count=50,
            start_offset=0,
            end_offset=50,
        )
        # Assign a mock UUID manually for document_id
        chunk.document_id = uuid4()

        mc = MessageCitation(document_chunk=chunk)

        # Test the ORM properties we implemented
        self.assertEqual(mc.document_id, chunk.document_id)
        self.assertEqual(mc.document_name, "notes.pdf")
        self.assertEqual(mc.page, "N/A")
        self.assertEqual(mc.score, 0.0)

        # Validate that CitationResponse parses it correctly using from_attributes=True
        citation_schema = CitationResponse.model_validate(mc)
        self.assertEqual(citation_schema.document_id, chunk.document_id)
        self.assertEqual(citation_schema.document_name, "notes.pdf")
        self.assertEqual(citation_schema.page, "N/A")
        self.assertEqual(citation_schema.score, 0.0)


if __name__ == "__main__":
    unittest.main()
