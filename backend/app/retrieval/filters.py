from app.vectorstore.schemas import SearchResult


class ResultFilter:

    @staticmethod
    def filter_by_score(results: list[SearchResult], min_score: float) -> list[SearchResult]:
        """Keep only results whose similarity score is >= min_score."""
        return [r for r in results if r.score >= min_score]

    @staticmethod
    def limit_results(results: list[SearchResult], max_results: int) -> list[SearchResult]:
        """Limit the number of results returned."""
        return results[:max_results]
