import unittest
from app.engine.schemas import PageObject, DiagramMetadata, TableMetadata, EquationMetadata
from app.engine.builder import MarkdownBuilder


class TestMarkdownBuilder(unittest.TestCase):

    def test_build_page_markdown_comprehensive(self):
        """Verify compiling a PageObject into a rich Unified Markdown page block."""
        page = PageObject(
            page_number=1,
            text="Operating System Cache Hierarchy",
            diagrams=[
                DiagramMetadata(
                    page_number=1,
                    title="Memory Architecture",
                    description="Illustrates CPU cache levels.",
                    mermaid_code="graph TD\n  CPU --> L1",
                    concepts=["CPU", "L1 Cache"],
                )
            ],
            tables=[
                TableMetadata(
                    page_number=1,
                    content_markdown="| Cache | Speed |\n| --- | --- |\n| L1 | 1ns |",
                )
            ],
            equations=[
                EquationMetadata(
                    page_number=1,
                    latex="T_{avg} = h \\cdot T_c",
                    explanation="Average access time equation.",
                )
            ],
        )

        md = MarkdownBuilder.build_page_markdown(page)

        self.assertIn("# Page 1", md)
        self.assertIn("Operating System Cache Hierarchy", md)
        self.assertIn("### Memory Architecture", md)
        self.assertIn("```mermaid", md)
        self.assertIn("| Cache | Speed |", md)
        self.assertIn("$$ T_{avg} = h \\cdot T_c $$", md)

    def test_build_document_markdown_multi_page(self):
        """Verify compiling multiple PageObjects into a single unified document."""
        p1 = PageObject(page_number=1, text="Page 1 Introduction")
        p2 = PageObject(page_number=2, text="Page 2 Advanced Topics")

        doc_md = MarkdownBuilder.build_document_markdown([p1, p2])

        self.assertIn("# Page 1", doc_md)
        self.assertIn("# Page 2", doc_md)
        self.assertIn("---", doc_md)


if __name__ == "__main__":
    unittest.main()
