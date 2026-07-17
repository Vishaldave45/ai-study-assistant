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
    DocumentChunkResponse,
    DocumentChunkPreviewItem,
    DocumentEmbedResponse,
)
from app.vectorstore.schemas import IndexResult
from app.retrieval.schemas import SearchRequest, SearchResponse, SearchResponseItem
from app.prompts.schemas import PromptRequest, PromptResponse
from app.pdf import (
    PDFParser,
    PDFParseError,
    PDFPasswordProtectedError,
    CorruptedPDFError,
    EmptyPDFError,
)
from app.text import TextProcessingPipeline, TextProcessingError
from app.services.document.document_service import DocumentService
from app.services.document.processing_service import DocumentProcessingService
from app.repositories.chunk_repository import ChunkRepository

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    description="Upload a PDF document (max 20MB) to a specified workspace.",
)
def upload_document(
    workspace_id: UUID = Form(
        ..., description="The workspace ID to upload the document to"
    ),
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
    query: str | None = Query(
        None, description="Search query matching original filename"
    ),
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


@router.post(
    "/{id}/chunk",
    response_model=DocumentChunkResponse,
    status_code=status.HTTP_200_OK,
    summary="Chunk document and persist in database",
    description="Loads the stored PDF, parses, cleans, splits into chunks, and saves to database. Returns summary stats and preview.",
)
def chunk_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentChunkResponse:
    # 1. Run the processing service to chunk and save to DB
    processing_service = DocumentProcessingService(db)

    try:
        processing_service.process_document(
            owner_id=current_user.id,
            document_id=id,
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
            detail=f"Failed to parse PDF: {str(exc)}",
        ) from exc
    except TextProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean text: {str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document chunks: {str(exc)}",
        ) from exc

    # 2. Retrieve chunks from DB to build response
    chunk_repo = ChunkRepository(db)
    chunks = chunk_repo.list_by_document(id)

    total_chunks = len(chunks)
    avg_tokens = (
        int(sum(c.token_count for c in chunks) / total_chunks)
        if total_chunks > 0
        else 0
    )

    # Return preview list (showing first 500 characters of each chunk)
    preview_items = [
        DocumentChunkPreviewItem(
            index=c.chunk_index,
            preview=c.content[:500],
        )
        for c in chunks
    ]

    return DocumentChunkResponse(
        total_chunks=total_chunks,
        average_tokens=avg_tokens,
        chunks=preview_items,
    )


@router.post(
    "/{id}/embed",
    response_model=DocumentEmbedResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate embeddings for document chunks",
    description="Runs the embedding pipeline on the document chunks, returning the model information and dimensions.",
)
def embed_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentEmbedResponse:
    from app.embedding.pipeline import EmbeddingPipeline

    pipeline = EmbeddingPipeline(db)

    try:
        results = pipeline.run_pipeline(
            owner_id=current_user.id,
            document_id=id,
        )

        # BAAI/bge-small-en-v1.5 details
        model_name = "BAAI/bge-small-en-v1.5"
        dimension = 384

        return DocumentEmbedResponse(
            chunks=len(results),
            dimension=dimension,
            model=model_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding pipeline failed: {str(exc)}",
        ) from exc


@router.post(
    "/{id}/index",
    response_model=IndexResult,
    status_code=status.HTTP_200_OK,
    summary="Index document chunks and persist in FAISS",
    description="Parses, chunks, embeds, and indexes the document into the workspace FAISS vector store.",
)
def index_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IndexResult:
    from app.vectorstore.service import VectorStoreService
    from app.vectorstore.exceptions import VectorStoreError
    from app.exceptions.workspace import (
        WorkspaceNotFoundError,
        WorkspaceAccessDeniedError,
    )
    from app.exceptions.document import DocumentNotFoundError, DocumentAccessDeniedError
    from app.pdf import (
        PDFPasswordProtectedError,
        CorruptedPDFError,
        EmptyPDFError,
        PDFParseError,
    )
    from app.text import TextProcessingError

    service = VectorStoreService(db)
    try:
        stats = service.index_document(
            owner_id=current_user.id,
            document_id=id,
        )
        return IndexResult(**stats)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DocumentAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WorkspaceAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
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
            detail=f"Failed to parse PDF: {str(exc)}",
        ) from exc
    except TextProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean text: {str(exc)}",
        ) from exc
    except VectorStoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector store indexing failed: {str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during indexing: {str(exc)}",
        ) from exc


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search across workspace document chunks",
    description="Retrieves the top matching document chunks for a natural language query in a workspace.",
)
def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    from app.repositories.workspace_repository import WorkspaceRepository
    from app.retrieval.service import RetrievalService
    from app.retrieval.exceptions import RetrievalError

    # Validate Workspace existence and ownership
    workspaces = WorkspaceRepository(db)
    workspace = workspaces.get_by_id(request.workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {request.workspace_id} not found.",
        )
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can access this workspace.",
        )

    service = RetrievalService(db)
    try:
        retrieval = service.retrieve(
            workspace_id=request.workspace_id,
            query=request.query,
        )
        results = [
            SearchResponseItem(
                chunk_id=UUID(chunk.chunk_id) if isinstance(chunk.chunk_id, str) else chunk.chunk_id,
                document_id=UUID(chunk.document_id) if isinstance(chunk.document_id, str) else chunk.document_id,
                score=chunk.score,
                content=chunk.text,
            )
            for chunk in retrieval.chunks
        ]
        return SearchResponse(query=retrieval.query, results=results)
    except RetrievalError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during search: {str(exc)}",
        ) from exc


@router.post(
    "/prompt",
    response_model=PromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Construct a RAG prompt for a natural language query",
    description="Retrieves matching chunks and builds a structured LLM prompt.",
)
def construct_prompt(
    request: PromptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PromptResponse:
    from sqlalchemy import select
    from app.repositories.workspace_repository import WorkspaceRepository
    from app.database.models.document import Document
    from app.retrieval.service import RetrievalService
    from app.prompts.builder import PromptBuilder
    from app.prompts.exceptions import PromptBuilderError, PromptTooLargeError

    # Validate Workspace existence and ownership
    workspaces = WorkspaceRepository(db)
    workspace = workspaces.get_by_id(request.workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {request.workspace_id} not found.",
        )
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can access this workspace.",
        )

    # 1. Retrieve chunks
    retrieval_service = RetrievalService(db)
    try:
        retrieval = retrieval_service.retrieve(
            workspace_id=request.workspace_id,
            query=request.query,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed during prompt construction: {str(exc)}",
        ) from exc

    # 2. Format context chunks using pre-resolved metadata
    chunks_for_builder = [
        {
            "content": res.text,
            "filename": res.metadata.get("original_filename", "Unknown Document"),
            "page": "N/A"
        }
        for res in retrieval.chunks
    ]

    # 4. Build the prompt
    builder = PromptBuilder()
    try:
        prompt_string = builder.build(request.query, chunks_for_builder)
        return PromptResponse(prompt=prompt_string)
    except PromptTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except PromptBuilderError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build prompt: {str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc
