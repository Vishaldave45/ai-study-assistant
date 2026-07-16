class ContextFormatter:

    @staticmethod
    def format_chunk(content: str, filename: str, page: str = "N/A") -> str:
        """
        Formats a chunk for embedding in the prompt context.
        """
        return (
            f"Document: {filename}\n"
            f"Page: {page}\n"
            f"Chunk:\n"
            f"{content}\n"
        )
