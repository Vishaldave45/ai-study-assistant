class CitationFormatter:

    @staticmethod
    def format_citation(filename: str, page: str = "N/A") -> str:
        """
        Formats a citation reference string.
        """
        return f"Source: {filename} Page {page}"
