class PDFParseError(Exception):
    """Base exception for PDF parsing errors."""

    pass


class PDFPasswordProtectedError(PDFParseError):
    """Raised when the PDF is password protected."""

    pass


class CorruptedPDFError(PDFParseError):
    """Raised when the PDF file is corrupted."""

    pass


class EmptyPDFError(PDFParseError):
    """Raised when the PDF file has no pages."""

    pass
