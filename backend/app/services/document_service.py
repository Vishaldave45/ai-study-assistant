import logging
import re
import uuid
from io import BytesIO
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.database.enums import DocumentStatus
from app.database.models.document import Document
from app.exceptions.document import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    FileSizeExceededError,
    InvalidFileTypeError,
)
from app.exceptions.workspace import (
    WorkspaceAccessDeniedError,
    WorkspaceNotFoundError,
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.storage import storage

logger = logging.getLogger(__name__)

# Maximum file size allowed: 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024


def get_pdf_page_count(data: bytes) -> int | None:
    """
    Attempt to extract the page count of a PDF by searching for the /Count key.
    Uses regex scanning of the binary PDF data to avoid external library dependencies.
    """
    try:
        # Scan for /Count key in the PDF structure
        counts = [int(m) for m in re.findall(b"/Count\s+(\d+)", data)]
        if counts:
            return max(counts)
    except Exception as e:
        logger.debug(f"Failed to parse page count from PDF: {e}")
    return None


class DocumentService:

    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)
        self.workspaces = WorkspaceRepository(db)

    def _validate_workspace_owner(self, workspace_id: UUID, owner_id: UUID) -> None:
        workspace = self.workspaces.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(f"Workspace with ID {workspace_id} not found.")
        if workspace.owner_id != owner_id:
            raise WorkspaceAccessDeniedError(
                "Only the owner can access this workspace."
            )

    def upload_document(
        self,
        owner_id: UUID,
        workspace_id: UUID,
        file: UploadFile,
    ) -> Document:
        # 1. Validate Workspace existence and ownership
        self._validate_workspace_owner(workspace_id, owner_id)

        # 2. Validate upload MIME type (only PDF accepted)
        if file.content_type != "application/pdf":
            raise InvalidFileTypeError("Only PDF documents are allowed.")

        # 3. Read content and validate file size (max 20MB)
        try:
            file_data = file.file.read()
        except Exception as e:
            raise ValueError(f"Failed to read uploaded file content: {str(e)}")

        file_size = len(file_data)
        if file_size > MAX_FILE_SIZE:
            raise FileSizeExceededError("File size exceeds the 20MB limit.")

        # 4. Generate unique stored filename
        stored_filename = f"{uuid.uuid4()}.pdf"
        storage_path = f"workspaces/{workspace_id}/{stored_filename}"

        # 5. Extract PDF metadata (page count)
        page_count = get_pdf_page_count(file_data)

        # 6. Save to storage provider
        data_buffer = BytesIO(file_data)
        storage.save(storage_path, data_buffer)

        # 7. Create database record
        document = Document(
            workspace_id=workspace_id,
            original_filename=file.filename or "document.pdf",
            stored_filename=stored_filename,
            mime_type="application/pdf",
            file_size=file_size,
            page_count=page_count,
            status=DocumentStatus.READY,
        )
        self.documents.add(document)

        # 8. Commit with rollback strategy
        try:
            self.db.commit()
            self.db.refresh(document)
            logger.info(f"Document uploaded: {document.id} in workspace {workspace_id}")
            return document
        except Exception as e:
            self.db.rollback()
            # Rollback storage operation to maintain consistency
            try:
                storage.delete(storage_path)
            except Exception as storage_err:
                logger.error(
                    f"Failed to delete stored file {storage_path} during rollback: {storage_err}"
                )
            raise e

    def get_document(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> Document:
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found.")

        # Validate that the requesting user owns the workspace containing this document
        self._validate_workspace_owner(document.workspace_id, owner_id)
        return document

    def get_document_stream(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> BytesIO:
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found.")

        # Validate workspace ownership
        self._validate_workspace_owner(document.workspace_id, owner_id)

        storage_path = f"workspaces/{document.workspace_id}/{document.stored_filename}"
        if not storage.exists(storage_path):
            raise FileNotFoundError(
                f"Physical file for document {document_id} not found on disk."
            )

        return storage.open(storage_path)

    def list_documents(
        self,
        owner_id: UUID,
        workspace_id: UUID,
        page: int = 1,
        page_size: int = 10,
        query: str | None = None,
    ) -> tuple[list[Document], int, int]:
        # Validate workspace ownership first
        self._validate_workspace_owner(workspace_id, owner_id)

        skip = (page - 1) * page_size
        limit = page_size

        total = self.documents.count(workspace_id=workspace_id, query=query)
        documents = self.documents.paginate(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
            query=query,
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return documents, total, total_pages

    def download_document(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> tuple[str, str]:
        """
        Validate ownership and return (absolute_file_path, original_filename)
        """
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found.")

        # Validate workspace ownership
        self._validate_workspace_owner(document.workspace_id, owner_id)

        storage_path = f"workspaces/{document.workspace_id}/{document.stored_filename}"
        if not storage.exists(storage_path):
            raise FileNotFoundError(
                f"Physical file for document {document_id} not found on disk."
            )

        # Resolve path
        if hasattr(storage, "_get_absolute_path"):
            file_path = str(storage._get_absolute_path(storage_path))
        else:
            file_path = str(storage.base_path / storage_path)

        return file_path, document.original_filename

    def delete_document(
        self,
        owner_id: UUID,
        document_id: UUID,
    ) -> None:
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found.")

        # Validate ownership
        self._validate_workspace_owner(document.workspace_id, owner_id)

        storage_path = f"workspaces/{document.workspace_id}/{document.stored_filename}"

        # Delete physical file first
        storage.delete(storage_path)

        # Soft-delete database record
        self.documents.delete(document)

        try:
            self.db.commit()
            logger.info(f"Document deleted: {document_id} by user {owner_id}")
        except Exception as e:
            self.db.rollback()
            raise e
