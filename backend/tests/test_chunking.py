import unittest
from uuid import uuid4
import fitz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from io import BytesIO

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.document import Document
from app.database.models.document_chunk import DocumentChunk
from app.database.enums import UserStatus, DocumentStatus
from app.services.document_processing_service import DocumentProcessingService
from app.repositories.chunk_repository import ChunkRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_chunking.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class TestChunkingEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()
        self.processing_service = DocumentProcessingService(self.db)
        self.chunk_repo = ChunkRepository(self.db)

        # Create dummy user, workspace, and document
        self.user_id = uuid4()
        user = User(
            id=self.user_id,
            email=f"chunk_user_{uuid4().hex[:6]}@example.com",
            full_name="Chunk Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(user)

        self.workspace_id = uuid4()
        workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Chunk Workspace",
        )
        self.db.add(workspace)

        self.document_id = uuid4()
        self.document = Document(
            id=self.document_id,
            workspace_id=self.workspace_id,
            original_filename="test.pdf",
            stored_filename="stored_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            status=DocumentStatus.READY,
        )
        self.db.add(self.document)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    @patch("app.services.document_service.DocumentService.get_document_stream")
    def test_document_processing_pipeline(self, mock_get_stream):
        # Create a sample PDF in memory with multiple lines to prevent page width clipping
        doc = fitz.open()
        page = doc.new_page()
        for y in range(50, 800, 20):
            page.insert_text((50, y), "Artificial Intelligence is the simulation of human intelligence processes by machines.")
        
        pdf_bytes = doc.write()
        doc.close()
        
        mock_get_stream.return_value = BytesIO(pdf_bytes)

        # Process document
        num_chunks = self.processing_service.process_document(
            owner_id=self.user_id,
            document_id=self.document_id,
        )

        self.assertGreater(num_chunks, 1)

        # Check DB persistence
        chunks = self.chunk_repo.list_by_document(self.document_id)
        self.assertEqual(len(chunks), num_chunks)
        
        # Verify first chunk details
        self.assertEqual(chunks[0].chunk_index, 0)
        self.assertIn("Artificial Intelligence", chunks[0].content)
        self.assertGreater(chunks[0].token_count, 0)
        self.assertEqual(chunks[0].start_offset, 0)

        # Verify document status updated to READY
        self.db.refresh(self.document)
        self.assertEqual(self.document.status, DocumentStatus.READY)

    @patch("app.services.document_service.DocumentService.get_document_stream")
    def test_reprocessing_deletes_old_chunks(self, mock_get_stream):
        # 1. First run
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "First processing run text.")
        pdf_bytes1 = doc.write()
        doc.close()
        
        mock_get_stream.return_value = BytesIO(pdf_bytes1)
        self.processing_service.process_document(self.user_id, self.document_id)

        # Verify chunks exist
        self.assertEqual(self.chunk_repo.count(self.document_id), 1)

        # 2. Second run with different text
        doc2 = fitz.open()
        page2 = doc2.new_page()
        page2.insert_text((50, 50), "Second run text.")
        pdf_bytes2 = doc2.write()
        doc2.close()

        mock_get_stream.return_value = BytesIO(pdf_bytes2)
        self.processing_service.process_document(self.user_id, self.document_id)

        # Verify old chunks were deleted and only 1 new chunk exists
        chunks = self.chunk_repo.list_by_document(self.document_id)
        self.assertEqual(len(chunks), 1)
        self.assertIn("Second run", chunks[0].content)


if __name__ == "__main__":
    unittest.main()
