import unittest
import fitz  # PyMuPDF
from app.engine.schemas import PageObject, ImageMetadata, DiagramMetadata
from app.engine.factory import DocumentProcessorFactory
from app.engine.processors.pdf import PDFDocumentProcessor


class TestDocumentEngine(unittest.TestCase):

    def test_page_object_schema_serialization(self):
        """Verify PageObject Pydantic schema validation and serialization."""
        page = PageObject(
            page_number=1,
            text="Operating Systems Overview",
            images=[
                ImageMetadata(
                    page_number=1,
                    bbox=[10.0, 20.0, 100.0, 200.0],
                    mime_type="image/png",
                    width=300,
                    height=400,
                )
            ],
            diagrams=[
                DiagramMetadata(
                    page_number=1,
                    title="Process Lifecycle",
                    concepts=["Ready", "Running", "Waiting", "Terminated"],
                )
            ],
        )

        data = page.model_dump()
        self.assertEqual(data["page_number"], 1)
        self.assertEqual(len(data["images"]), 1)
        self.assertEqual(data["images"][0]["width"], 300)
        self.assertEqual(data["diagrams"][0]["title"], "Process Lifecycle")

    def test_factory_processor_resolution(self):
        """Verify DocumentProcessorFactory resolves correct strategy by MIME type or extension."""
        pdf_proc = DocumentProcessorFactory.get_processor("application/pdf")
        self.assertIsInstance(pdf_proc, PDFDocumentProcessor)

        ext_proc = DocumentProcessorFactory.get_processor("pdf")
        self.assertIsInstance(ext_proc, PDFDocumentProcessor)

        with self.assertRaises(ValueError):
            DocumentProcessorFactory.get_processor("unsupported_format")

    def test_pdf_processor_pymupdf_extraction(self):
        """Verify PDFDocumentProcessor extracts text and page structure from an in-memory PDF."""
        # Create a simple 2-page in-memory PDF using PyMuPDF
        doc = fitz.open()
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((50, 50), "Page 1: Introduction to Computer Architecture")

        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((50, 50), "Page 2: Memory Hierarchy and Cache Organization")

        pdf_bytes = doc.tobytes()
        doc.close()

        processor = PDFDocumentProcessor()
        page_objects = processor.process(pdf_bytes)

        self.assertEqual(len(page_objects), 2)
        self.assertEqual(page_objects[0].page_number, 1)
        self.assertIn("Introduction to Computer Architecture", page_objects[0].text)
        self.assertEqual(page_objects[1].page_number, 2)
        self.assertIn("Memory Hierarchy", page_objects[1].text)


if __name__ == "__main__":
    unittest.main()
