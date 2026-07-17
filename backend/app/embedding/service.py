import logging
from app.embedding.models import SentenceTransformerProvider
from app.embedding.config import EMBEDDING_BATCH_SIZE
from app.embedding.schemas import EmbeddingResult

logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(self):
        self.provider = SentenceTransformerProvider()

    def generate_embeddings(self, texts: list[str]) -> list[EmbeddingResult]:
        if not texts:
            return []

        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        results = []
        batch_size = EMBEDDING_BATCH_SIZE

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            try:
                batch_vectors = self.provider.embed_batch(batch_texts)
                for text, vector in zip(batch_texts, batch_vectors):
                    results.append(
                        EmbeddingResult(
                            text=text,
                            vector=vector,
                            dimension=self.provider.dimension(),
                            model=self.provider.model_name(),
                        )
                    )
            except Exception as exc:
                logger.error(
                    f"Failed to generate embeddings batch starting at index {i}: {exc}"
                )
                raise

        logger.info("Successfully generated all embeddings.")
        return results
