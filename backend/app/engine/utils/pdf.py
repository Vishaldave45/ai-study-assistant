import re
import fitz


class PDFParseError(Exception):
    """Base exception for PDF parsing failures."""
    pass


class PDFPasswordProtectedError(PDFParseError):
    """Raised when PDF is password protected."""
    pass


class CorruptedPDFError(PDFParseError):
    """Raised when PDF file is corrupted."""
    pass


class EmptyPDFError(PDFParseError):
    """Raised when PDF has 0 pages."""
    pass


def is_pdf(filename: str) -> bool:
    """Check if filename ends with .pdf."""
    return filename.lower().endswith(".pdf")


def normalize_filename(filename: str) -> str:
    """Normalize filename by converting to lowercase and underscores."""
    if not filename:
        return "document.pdf"

    parts = filename.rsplit(".", 1)
    name = parts[0]
    ext = parts[1] if len(parts) > 1 else "pdf"

    name_clean = re.sub(r"[^\w\s-]", "", name)
    name_clean = re.sub(r"[\s-]+", "_", name_clean).strip("_").lower()

    return f"{name_clean or 'document'}.{ext.lower()}"


def safe_open_pdf(stream: bytes) -> fitz.Document:
    """Open a PDF from bytes stream and validate integrity."""
    try:
        doc = fitz.open(stream=stream, filetype="pdf")
    except Exception as exc:
        raise CorruptedPDFError("The PDF file is corrupted and cannot be opened.") from exc

    if doc.is_encrypted:
        doc.close()
        raise PDFPasswordProtectedError("The PDF file is password-protected.")

    if len(doc) == 0:
        doc.close()
        raise EmptyPDFError("The PDF file contains no pages.")

    return doc
