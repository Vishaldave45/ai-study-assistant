from sentence_transformers import SentenceTransformer
from app.embedding.provider import EmbeddingProvider
from app.embedding.config import (
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    EMBEDDING_NORMALIZE,
)
from app.embedding.exceptions import EmbeddingModelError, EmbeddingGenerationError


class SentenceTransformerProvider(EmbeddingProvider):

    def __init__(self):
        try:
            self._model = SentenceTransformer(
                EMBEDDING_MODEL,
                device=EMBEDDING_DEVICE,
            )
        except Exception as exc:
            raise EmbeddingModelError(
                f"Failed to load sentence transformer model '{EMBEDDING_MODEL}': {exc}"
            ) from exc

    def embed(self, text: str) -> list[float]:
        if not text:
            return []
        try:
            vector = self._model.encode(
                text,
                normalize_embeddings=EMBEDDING_NORMALIZE,
            )
            return vector.tolist()
        except Exception as exc:
            raise EmbeddingGenerationError(
                f"Failed to generate embedding: {exc}"
            ) from exc

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = self._model.encode(
                texts,
                normalize_embeddings=EMBEDDING_NORMALIZE,
            )
            return vectors.tolist()
        except Exception as exc:
            raise EmbeddingGenerationError(
                f"Failed to generate batch embeddings: {exc}"
            ) from exc

    def dimension(self) -> int:
        return 384

    def model_name(self) -> str:
        return EMBEDDING_MODEL
