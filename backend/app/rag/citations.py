from app.rag.schemas import CitationItem


class CitationFormatter:

    @staticmethod
    def format_citation(filename: str, score: float, page: str = "N/A") -> CitationItem:
        """
        Structures citation metadata into a CitationItem response DTO.
        """
        return CitationItem(
            document=filename,
            page=page,
            score=round(float(score), 4),
        )
