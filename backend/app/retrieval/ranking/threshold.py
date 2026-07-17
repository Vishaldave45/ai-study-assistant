from app.retrieval.models import RetrievedChunk


class ThresholdFilter:

    @staticmethod
    def filter_by_score(
        chunks: list[RetrievedChunk], min_score: float
    ) -> list[RetrievedChunk]:
        """Keep only chunks whose similarity score is >= min_score."""
        return [c for c in chunks if c.score >= min_score]
