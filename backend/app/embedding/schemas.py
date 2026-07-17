from app.schemas.base import BaseSchema


class EmbeddingResult(BaseSchema):
    text: str
    vector: list[float]
    dimension: int
    model: str


class EmbeddingBatch(BaseSchema):
    results: list[EmbeddingResult]
    count: int
