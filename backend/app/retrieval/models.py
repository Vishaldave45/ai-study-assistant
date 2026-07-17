from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievedChunk:
    """
    Single retrieved document chunk.
    """

    chunk_id: str
    document_id: str
    text: str
    score: float
    page: int
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalResult:
    """
    Final retrieval output.
    """

    query: str
    chunks: list[RetrievedChunk]
    context_text: str | None = None
    citations: list[str] = field(default_factory=list)
