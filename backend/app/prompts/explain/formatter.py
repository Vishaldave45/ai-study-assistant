from app.prompts.shared.formatter import ContextFormatter

class ExplainFormatter:

    @staticmethod
    def format_chunks(chunks: list[dict]) -> list[str]:
        """
        Formats a list of chunk dicts into structured context strings.
        Each chunk must have 'content' and 'filename', and optionally 'page'.
        """
        formatted_chunks = []
        for chunk in chunks:
            formatted_chunks.append(
                ContextFormatter.format_chunk(
                    content=chunk["content"],
                    filename=chunk["filename"],
                    page=chunk.get("page", "N/A"),
                )
            )
        return formatted_chunks
