import logging
from app.engine.schemas import PageObject

logger = logging.getLogger(__name__)


class MarkdownBuilder:
    """
    Unified Markdown Builder reconstructing PageObject instances into rich,
    structured Markdown documents containing text, Mermaid diagrams, Markdown tables,
    and LaTeX equations.
    """

    @staticmethod
    def build_page_markdown(page: PageObject) -> str:
        """
        Builds a single Markdown document block for a PageObject.
        """
        lines: list[str] = [f"# Page {page.page_number}", ""]

        # 1. Main Page Text Content
        if page.text and page.text.strip():
            lines.append("## Text Content")
            lines.append(page.text.strip())
            lines.append("")

        # 2. Parsed Diagrams & Mermaid Code
        if page.diagrams:
            lines.append("## Visual Diagrams")
            for diag in page.diagrams:
                if diag.title:
                    lines.append(f"### {diag.title}")
                if diag.description:
                    lines.append(f"*{diag.description}*")
                    lines.append("")
                if diag.mermaid_code:
                    lines.append("```mermaid")
                    lines.append(diag.mermaid_code.strip())
                    lines.append("```")
                    lines.append("")
                if diag.concepts:
                    lines.append(f"**Concepts**: {', '.join(diag.concepts)}")
                    lines.append("")

        # 3. Formatted Tables
        if page.tables:
            lines.append("## Data Tables")
            for table in page.tables:
                if table.content_markdown:
                    lines.append(table.content_markdown.strip())
                    lines.append("")

        # 4. Equations & LaTeX
        if page.equations:
            lines.append("## Mathematical Formulas")
            for eq in page.equations:
                lines.append(f"$$ {eq.latex} $$")
                if eq.explanation:
                    lines.append(f"*{eq.explanation}*")
                lines.append("")

        return "\n".join(lines).strip()

    @classmethod
    def build_document_markdown(cls, pages: list[PageObject]) -> str:
        """
        Compiles an entire list of PageObjects into a single unified Markdown document.
        """
        page_markdowns = [cls.build_page_markdown(page) for page in pages]
        return "\n\n---\n\n".join(page_markdowns)
