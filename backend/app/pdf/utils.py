from __future__ import annotations

import re
import fitz
from app.pdf.exceptions import CorruptedPDFError, PDFPasswordProtectedError, EmptyPDFError


def is_pdf(filename: str) -> bool:
    """Check if the filename ends with .pdf (case-insensitive)."""
    return filename.lower().endswith(".pdf")


def normalize_filename(filename: str) -> str:
    """Normalize the filename by converting to lowercase, removing non-alphanumeric characters,
    and replacing spaces with underscores, keeping the extension.
    """
    if not filename:
        return "document.pdf"
    
    parts = filename.rsplit(".", 1)
    name = parts[0]
    ext = parts[1] if len(parts) > 1 else "pdf"
    
    # Remove non-alphanumeric characters except spaces, dashes, and underscores
    name_clean = re.sub(r"[^\w\s-]", "", name)
    # Replace spaces and dashes with underscores, clean consecutive underscores
    name_clean = re.sub(r"[\s-]+", "_", name_clean).strip("_").lower()
    
    return f"{name_clean or 'document'}.{ext.lower()}"


def safe_open_pdf(stream: bytes) -> fitz.Document:
    """Open a PDF from bytes stream and validate it."""
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
