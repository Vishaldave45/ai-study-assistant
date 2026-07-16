from app.vectorstore.schemas import SearchResult


class ScoreRanker:

    @staticmethod
    def rank(results: list[SearchResult]) -> list[SearchResult]:
        """Rank results by score in descending order."""
        return sorted(results, key=lambda x: x.score, reverse=True)
