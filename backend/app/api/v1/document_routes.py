from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.dependencies.auth import get_current_user
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
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    MessageResponse,
    DocumentParsePreviewResponse,
    DocumentCleanPreviewResponse,
)
from app.pdf import PDFParser, PDFParseError, PDFPasswordProtectedError, CorruptedPDFError, EmptyPDFError
from app.text import TextProcessingPipeline, TextProcessingError
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    description="Upload a PDF document (max 20MB) to a specified workspace.",
)
def upload_document(
    workspace_id: UUID = Form(..., description="The workspace ID to upload the document to"),
    file: UploadFile = File(..., description="The PDF file to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    service = DocumentService(db)
    try:
        document = service.upload_document(
            owner_id=current_user.id,
            workspace_id=workspace_id,
            file=file,
        )
        return DocumentResponse.model_validate(document)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except FileSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during upload: {str(exc)}",
        ) from exc


@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List workspace documents",
    description="List active documents inside a workspace with pagination and optional query filtering.",
)
def list_documents(
    workspace_id: UUID = Query(..., description="Filter documents by workspace ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    query: str | None = Query(None, description="Search query matching original filename"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    service = DocumentService(db)
    try:
        documents, total, total_pages = service.list_documents(
            owner_id=current_user.id,
            workspace_id=workspace_id,
            page=page,
            page_size=page_size,
            query=query,
        )
        return DocumentListResponse(
            items=documents,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details",
    description="Retrieve metadata for a specific document by its ID.",
)
def get_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    service = DocumentService(db)
    try:
        document = service.get_document(
            owner_id=current_user.id,
            document_id=id,
        )
        return DocumentResponse.model_validate(document)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{id}/download",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Download document file",
    description="Stream the physical PDF file for download.",
)
def download_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    service = DocumentService(db)
    try:
        file_path, original_filename = service.download_document(
            owner_id=current_user.id,
            document_id=id,
        )
        return FileResponse(
            path=file_path,
            filename=original_filename,
            media_type="application/pdf",
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a document",
    description="Delete the physical file and soft-delete the document record from the database.",
)
def delete_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = DocumentService(db)
    try:
        service.delete_document(
            owner_id=current_user.id,
            document_id=id,
        )
        return MessageResponse(message="Document deleted successfully.")
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/{id}/parse",
    response_model=DocumentParsePreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse document content (Preview)",
    description="Loads the stored PDF, parses it, and returns extracted metadata and a 500 character text preview.",
)
def parse_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentParsePreviewResponse:
    service = DocumentService(db)
    try:
        # Load the stored file stream (BytesIO)
        stream = service.get_document_stream(
            owner_id=current_user.id,
            document_id=id,
        )
        
        # Parse it
        parsed_pdf = PDFParser.parse(stream.getvalue())
        
        # Build preview response (first 500 characters)
        text_preview = parsed_pdf.text[:500]
        
        return DocumentParsePreviewResponse(
            title=parsed_pdf.title,
            author=parsed_pdf.author,
            page_count=parsed_pdf.page_count,
            text_preview=text_preview,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PDFPasswordProtectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot parse password-protected PDF: {str(exc)}",
        ) from exc
    except (CorruptedPDFError, EmptyPDFError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid PDF file: {str(exc)}",
        ) from exc
    except PDFParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse PDF file: {str(exc)}",
        ) from exc


@router.post(
    "/{id}/clean",
    response_model=DocumentCleanPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Clean and normalize document content (Preview)",
    description="Loads the stored PDF, parses it, processes the text, and returns cleaning statistics and a 500 character text preview.",
)
def clean_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentCleanPreviewResponse:
    service = DocumentService(db)
    try:
        # Load the stored file stream (BytesIO)
        stream = service.get_document_stream(
            owner_id=current_user.id,
            document_id=id,
        )
        
        # Parse PDF to get raw text
        parsed_pdf = PDFParser.parse(stream.getvalue())
        
        # Run text processing pipeline
        processed = TextProcessingPipeline.process(parsed_pdf.text)
        
        # Preview is first 500 characters
        preview = processed.text[:500]
        
        return DocumentCleanPreviewResponse(
            characters=processed.character_count,
            words=processed.word_count,
            preview=preview,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PDFPasswordProtectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot parse password-protected PDF: {str(exc)}",
        ) from exc
    except (CorruptedPDFError, EmptyPDFError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid PDF file: {str(exc)}",
        ) from exc
    except PDFParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse PDF file: {str(exc)}",
        ) from exc
    except TextProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean text: {str(exc)}",
        ) from exc
