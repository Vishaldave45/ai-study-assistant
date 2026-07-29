import unittest
from app.engine.schemas import PageObject, DiagramMetadata, TableMetadata, EquationMetadata
from app.engine.chunker import SmartSemanticChunker


class TestSmartChunker(unittest.TestCase):

    def test_chunk_page_typed_boundaries(self):
        """Verify chunk_page creates distinct typed chunks for text, diagrams, tables, and equations."""
        page = PageObject(
            page_number=1,
            text="First paragraph text.\n\nSecond paragraph text.",
            diagrams=[
                DiagramMetadata(
                    page_number=1,
                    title="OSI Model",
                    mermaid_code="graph TD\n App --> Pres",
                    concepts=["Application"],
                )
            ],
            tables=[
                TableMetadata(
                    page_number=1,
                    content_markdown="| Col 1 | Col 2 |\n| --- | --- |\n| Val 1 | Val 2 |",
                )
            ],
            equations=[
                EquationMetadata(
                    page_number=1,
                    latex="E = mc^2",
                    explanation="Mass-energy equivalence.",
                )
            ],
        )

        chunks = SmartSemanticChunker.chunk_page(page)

        # Expect 1 heading + 2 paragraphs + 1 diagram + 1 table + 1 equation = 6 chunks
        self.assertEqual(len(chunks), 6)

        types = [c.chunk_type for c in chunks]
        self.assertEqual(types, ["heading", "paragraph", "paragraph", "diagram", "table", "equation"])

        # Check diagram chunk contents
        diag_chunk = next(c for c in chunks if c.chunk_type == "diagram")
        self.assertIn("Diagram: OSI Model", diag_chunk.content)
        self.assertIn("graph TD", diag_chunk.content)
        self.assertEqual(diag_chunk.metadata["title"], "OSI Model")

        # Check table chunk integrity (table rows preserved intact)
        table_chunk = next(c for c in chunks if c.chunk_type == "table")
        self.assertIn("| Col 1 | Col 2 |", table_chunk.content)

        # Check equation chunk
        eq_chunk = next(c for c in chunks if c.chunk_type == "equation")
        self.assertIn("$$ E = mc^2 $$", eq_chunk.content)

    def test_chunk_document_multi_page(self):
        """Verify chunk_document processes multi-page documents."""
        p1 = PageObject(page_number=1, text="Page 1 Content")
        p2 = PageObject(page_number=2, text="Page 2 Content")

        all_chunks = SmartSemanticChunker.chunk_document([p1, p2])

        self.assertEqual(len(all_chunks), 4)  # 2 headings + 2 paragraphs
        page_nums = [c.page_number for c in all_chunks]
        self.assertEqual(page_nums, [1, 1, 2, 2])


if __name__ == "__main__":
    unittest.main()
