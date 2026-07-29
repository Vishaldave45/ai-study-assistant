from pathlib import Path
from app.engine.base import BaseDocumentProcessor
from app.engine.processors.pdf import PDFDocumentProcessor


class DocumentProcessorFactory:
    """
    Factory Pattern resolving the appropriate BaseDocumentProcessor strategy
    based on MIME type, filename, or file extension.
    """

    _processors = {
        "application/pdf": PDFDocumentProcessor,
        "pdf": PDFDocumentProcessor,
    }

    @classmethod
    def get_processor(cls, mime_or_ext: str) -> BaseDocumentProcessor:
        raw = mime_or_ext.lower().strip()
        if "/" in raw:
            key = raw
        elif "." in raw:
            key = raw.rsplit(".", 1)[-1]
        else:
            key = raw

        processor_class = cls._processors.get(key)
        if not processor_class:
            raise ValueError(f"Unsupported document format: {mime_or_ext}")
        return processor_class()

    @classmethod
    def register_processor(cls, format_key: str, processor_class: type[BaseDocumentProcessor]) -> None:
        cls._processors[format_key.lower().strip(".")] = processor_class
