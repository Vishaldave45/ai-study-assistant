from app.retrieval.models import RetrievedChunk
from app.prompts.shared.budget import TokenBudgetManager


class ContextBuilder:

    @staticmethod
    def build_context(
        chunks: list[RetrievedChunk],
        doc_map: dict[str, str],
        max_tokens: int = 4000,
    ) -> tuple[str, list[str], list[RetrievedChunk]]:
        """
        Merge retrieved chunks into a single context string, removing duplicates,
        building clean citations, and ensuring the content fits within the token budget.
        """
        seen_chunk_ids = set()
        unique_chunks = []
        for c in chunks:
            if c.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(c.chunk_id)
                unique_chunks.append(c)

        budget_manager = TokenBudgetManager(max_tokens=max_tokens)
        selected_chunks = []
        formatted_parts = []
        citations = []

        current_tokens = 0
        for idx, chunk in enumerate(unique_chunks, 1):
            doc_name = doc_map.get(str(chunk.document_id), "Unknown Source")
            citation_label = f"[{idx}] {doc_name} (Page {chunk.page})"

            part_text = f"--- Document Chunk {idx} ({doc_name}) ---\n{chunk.text}\n\n"
            part_tokens = budget_manager.count_tokens(part_text)

            if current_tokens + part_tokens > max_tokens:
                break

            current_tokens += part_tokens
            selected_chunks.append(chunk)
            formatted_parts.append(part_text)
            citations.append(citation_label)

        context_text = "".join(formatted_parts)
        return context_text, citations, selected_chunks
