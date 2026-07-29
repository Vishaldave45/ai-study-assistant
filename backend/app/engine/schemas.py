from uuid import uuid4
from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    image_id: str = Field(default_factory=lambda: str(uuid4()))
    page_number: int
    bbox: list[float] = Field(default_factory=list)  # [x0, y0, x1, y1]
    mime_type: str = "image/png"
    storage_path: str | None = None
    width: int = 0
    height: int = 0


class TableMetadata(BaseModel):
    table_id: str = Field(default_factory=lambda: str(uuid4()))
    page_number: int
    bbox: list[float] = Field(default_factory=list)
    content_markdown: str | None = None


class DiagramMetadata(BaseModel):
    diagram_id: str = Field(default_factory=lambda: str(uuid4()))
    page_number: int
    bbox: list[float] = Field(default_factory=list)
    title: str | None = None
    description: str | None = None
    mermaid_code: str | None = None
    concepts: list[str] = Field(default_factory=list)
    relationships: list[dict] = Field(default_factory=list)


class EquationMetadata(BaseModel):
    equation_id: str = Field(default_factory=lambda: str(uuid4()))
    page_number: int
    latex: str
    explanation: str | None = None


class PageObject(BaseModel):
    page_number: int
    text: str
    images: list[ImageMetadata] = Field(default_factory=list)
    tables: list[TableMetadata] = Field(default_factory=list)
    diagrams: list[DiagramMetadata] = Field(default_factory=list)
    equations: list[EquationMetadata] = Field(default_factory=list)
