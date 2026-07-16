import unittest
import fitz
from app.pdf.parser import PDFParser
from app.pdf.exceptions import CorruptedPDFError, EmptyPDFError
from app.pdf.utils import is_pdf, normalize_filename


class TestPDFParser(unittest.TestCase):

    def test_is_pdf(self):
        self.assertTrue(is_pdf("test.pdf"))
        self.assertTrue(is_pdf("TEST.PDF"))
        self.assertFalse(is_pdf("test.txt"))

    def test_normalize_filename(self):
        self.assertEqual(normalize_filename("My File Name.pdf"), "my_file_name.pdf")
        self.assertEqual(
            normalize_filename("Deep Learning!! (2).PDF"), "deep_learning_2.pdf"
        )
        self.assertEqual(normalize_filename(""), "document.pdf")

    def test_parse_valid_pdf(self):
        # Create a simple PDF in memory using fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Hello World from Antigravity")

        # Set some metadata
        doc.set_metadata(
            {
                "title": "Test Title",
                "author": "Antigravity",
            }
        )

        pdf_bytes = doc.write()
        doc.close()

        # Parse it
        parsed = PDFParser.parse(pdf_bytes)

        self.assertEqual(parsed.title, "Test Title")
        self.assertEqual(parsed.author, "Antigravity")
        self.assertEqual(parsed.page_count, 1)
        self.assertIn("Hello World", parsed.text)

    def test_parse_empty_pdf_raises_error(self):
        import unittest.mock as mock

        mock_doc = mock.MagicMock()
        mock_doc.is_encrypted = False
        mock_doc.__len__.return_value = 0

        with mock.patch("fitz.open", return_value=mock_doc):
            with self.assertRaises(EmptyPDFError):
                PDFParser.parse(b"dummy bytes")

    def test_parse_corrupted_pdf_raises_error(self):
        corrupted_bytes = b"not a pdf file content at all"
        with self.assertRaises(CorruptedPDFError):
            PDFParser.parse(corrupted_bytes)


if __name__ == "__main__":
    unittest.main()
