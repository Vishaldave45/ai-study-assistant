import unittest
import tempfile
from uuid import uuid4
from unittest.mock import patch, MagicMock
from io import BytesIO

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.enums import UserStatus, DocumentStatus
from app.services.document.document_service import DocumentService


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_upload_indexing_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestUploadIndexing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()

        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_patcher = patch(
            "app.services.document.document_service.storage"
        )
        self.mock_storage = self.storage_patcher.start()

        # Create test owner & workspace
        self.user_id = uuid4()
        self.user = User(
            id=self.user_id,
            email=f"upload_user_{uuid4().hex[:6]}@example.com",
            full_name="Upload Tester",
            password_hash="fakehash",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        self.db.add(self.user)

        self.workspace_id = uuid4()
        self.workspace = Workspace(
            id=self.workspace_id,
            owner_id=self.user_id,
            name="Upload Workspace",
        )
        self.db.add(self.workspace)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.storage_patcher.stop()
        self.temp_dir.cleanup()

    @patch("app.vectorstore.service.VectorStoreService.index_document")
    def test_upload_document_success_transitions_to_ready(self, mock_index_doc):
        """
        Verify uploading a PDF triggers auto-indexing and transitions document status to READY.
        """
        mock_index_doc.return_value = {"chunks": 5, "vectors": 5, "dimension": 384}

        fake_file = MagicMock()
        fake_file.filename = "syllabus.pdf"
        fake_file.content_type = "application/pdf"
        fake_file.file.read.return_value = b"%PDF-1.4 Fake PDF Content /Count 3"

        service = DocumentService(self.db)
        doc = service.upload_document(self.user_id, self.workspace_id, fake_file)

        mock_index_doc.assert_called_once_with(owner_id=self.user_id, document_id=doc.id)
        self.assertEqual(doc.status, DocumentStatus.READY)

    @patch("app.vectorstore.service.VectorStoreService.index_document")
    def test_upload_document_indexing_failure_transitions_to_failed(self, mock_index_doc):
        """
        Verify indexing failure marks document status as FAILED without raising an unhandled exception.
        """
        mock_index_doc.side_effect = Exception("FAISS VectorStore Out Of Memory")

        fake_file = MagicMock()
        fake_file.filename = "corrupted.pdf"
        fake_file.content_type = "application/pdf"
        fake_file.file.read.return_value = b"%PDF-1.4 Corrupted Content"

        service = DocumentService(self.db)
        doc = service.upload_document(self.user_id, self.workspace_id, fake_file)

        self.assertEqual(doc.status, DocumentStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
