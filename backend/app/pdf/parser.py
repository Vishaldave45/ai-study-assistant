from __future__ import annotations

import fitz
from app.pdf.exceptions import PDFParseError
from app.pdf.schemas import ParsedPDF
from app.pdf.utils import safe_open_pdf
from app.pdf.metadata import extract_metadata, extract_page_count


class PDFParser:

    @classmethod
    def parse(cls, stream: bytes) -> ParsedPDF:
        """Parses a PDF from a bytes stream and extracts metadata, page count, and text."""
        doc = safe_open_pdf(stream)
        try:
            metadata = extract_metadata(doc)
            page_count = extract_page_count(doc)

            # Extract text from all pages
            text_pages = []
            for page in doc:
                page_text = page.get_text() or ""
                text_pages.append(page_text)
            
            combined_text = "\n".join(text_pages)

            return ParsedPDF(
                title=metadata.get("title") or None,
                author=metadata.get("author") or None,
                subject=metadata.get("subject") or None,
                creator=metadata.get("creator") or None,
                producer=metadata.get("producer") or None,
                keywords=metadata.get("keywords") or None,
                page_count=page_count,
                text=combined_text,
                metadata=metadata,
            )
        except Exception as exc:
            if not isinstance(exc, PDFParseError):
                raise PDFParseError(f"Error parsing PDF document: {str(exc)}") from exc
            raise
        finally:
            doc.close()
            
