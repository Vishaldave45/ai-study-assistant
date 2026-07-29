import logging
from typing import Literal
from pydantic import BaseModel, Field
from app.engine.schemas import PageObject

logger = logging.getLogger(__name__)

ChunkType = Literal["heading", "paragraph", "diagram", "table", "equation"]


class SemanticChunk(BaseModel):
    chunk_id: str | None = None
    page_number: int
    chunk_type: ChunkType
    content: str
    metadata: dict = Field(default_factory=dict)


class SmartSemanticChunker:
    """
    Structure-Aware Semantic Chunker splitting document PageObjects into
    heading, paragraph, diagram, table, and equation chunks.
    """

    @classmethod
    def chunk_page(cls, page: PageObject) -> list[SemanticChunk]:
        chunks: list[SemanticChunk] = []

        # 1. Page Heading Chunk
        chunks.append(
            SemanticChunk(
                page_number=page.page_number,
                chunk_type="heading",
                content=f"Page {page.page_number}",
                metadata={"page_number": page.page_number},
            )
        )

        # 2. Text Paragraph Chunks
        if page.text and page.text.strip():
            paragraphs = [p.strip() for p in page.text.split("\n\n") if p.strip()]
            for para in paragraphs:
                chunks.append(
                    SemanticChunk(
                        page_number=page.page_number,
                        chunk_type="paragraph",
                        content=para,
                        metadata={"page_number": page.page_number},
                    )
                )

        # 3. Diagram Chunks
        for diag in page.diagrams:
            diag_text = f"Diagram: {diag.title or 'Untitled'}\nDescription: {diag.description or ''}"
            if diag.mermaid_code:
                diag_text += f"\n```mermaid\n{diag.mermaid_code}\n```"
            chunks.append(
                SemanticChunk(
                    page_number=page.page_number,
                    chunk_type="diagram",
                    content=diag_text.strip(),
                    metadata={
                        "page_number": page.page_number,
                        "diagram_id": diag.diagram_id,
                        "title": diag.title,
                        "concepts": diag.concepts,
                    },
                )
            )

        # 4. Table Chunks (Keeps tables intact without splitting rows)
        for table in page.tables:
            if table.content_markdown:
                chunks.append(
                    SemanticChunk(
                        page_number=page.page_number,
                        chunk_type="table",
                        content=table.content_markdown.strip(),
                        metadata={
                            "page_number": page.page_number,
                            "table_id": table.table_id,
                        },
                    )
                )

        # 5. Equation Chunks
        for eq in page.equations:
            eq_text = f"$$ {eq.latex} $$"
            if eq.explanation:
                eq_text += f"\nExplanation: {eq.explanation}"
            chunks.append(
                SemanticChunk(
                    page_number=page.page_number,
                    chunk_type="equation",
                    content=eq_text.strip(),
                    metadata={
                        "page_number": page.page_number,
                        "equation_id": eq.equation_id,
                        "latex": eq.latex,
                    },
                )
            )

        return chunks

    @classmethod
    def chunk_document(cls, pages: list[PageObject]) -> list[SemanticChunk]:
        """
        Chunks an entire document of PageObjects into structure-aware semantic chunks.
        """
        all_chunks: list[SemanticChunk] = []
        for page in pages:
            all_chunks.extend(cls.chunk_page(page))
        return all_chunks
