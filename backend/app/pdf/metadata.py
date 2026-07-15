from __future__ import annotations

import fitz


def extract_metadata(doc: fitz.Document) -> dict:
    """Extract standard metadata fields from a PyMuPDF document."""
    return doc.metadata or {}


def extract_page_count(doc: fitz.Document) -> int:
    """Extract the total page count from a PyMuPDF document."""
    return len(doc)
