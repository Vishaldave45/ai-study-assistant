from app.chunking.schemas import DocumentChunkSchema
from app.chunking.splitter import TextSplitter
from app.chunking.tokenizer import TokenCounter


class ChunkingPipeline:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.splitter = TextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_text(self, text: str) -> list[DocumentChunkSchema]:
        if not text:
            return []

        # Split text into chunks
        chunk_contents = self.splitter.split_text(text)

        # Track start and end offsets dynamically by searching original text
        offsets = []
        search_start = 0
        for chunk in chunk_contents:
            start_idx = text.find(chunk, search_start)
            if start_idx == -1:
                # Fallback to search_start if index is not found
                start_idx = search_start

            end_idx = start_idx + len(chunk)
            offsets.append((start_idx, end_idx))
            # Advance search_start to avoid duplicate matches
            search_start = start_idx + 1

        # Build schemas
        chunk_schemas = []
        for idx, (content, (start_offset, end_offset)) in enumerate(
            zip(chunk_contents, offsets)
        ):
            token_count = TokenCounter.count_tokens(content)
            chunk_schemas.append(
                DocumentChunkSchema(
                    index=idx,
                    content=content,
                    character_count=len(content),
                    token_count=token_count,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )

        return chunk_schemas
