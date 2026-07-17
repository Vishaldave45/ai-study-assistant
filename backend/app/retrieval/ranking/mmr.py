import numpy as np
from app.retrieval.models import RetrievedChunk


class MMRRanker:

    @staticmethod
    def rank(
        query_embedding: list[float],
        chunks: list[RetrievedChunk],
        chunk_embeddings: dict[str, list[float]],
        lambda_val: float = 0.5,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """
        Perform MMR (Maximal Marginal Relevance) ranking on candidate chunks.

        - query_embedding: Vector representation of the query.
        - chunks: List of RetrievedChunk candidates.
        - chunk_embeddings: Dict mapping chunk_id (str) to vector representation (list[float]).
        - lambda_val: Diversity/relevance balance parameter.
                      1.0 = Pure relevance, 0.0 = Pure diversity.
        - top_k: Number of chunks to select.
        """
        if not chunks or top_k <= 0:
            return []

        # Filter out chunks that do not have embeddings
        valid_chunks = [c for c in chunks if c.chunk_id in chunk_embeddings]
        if not valid_chunks:
            return chunks[:top_k]

        q = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm > 0:
            q = q / q_norm

        # Prepare candidate embeddings matrix
        candidate_ids = [c.chunk_id for c in valid_chunks]
        cand_embeds = []
        for cid in candidate_ids:
            emb = np.array(chunk_embeddings[cid], dtype=np.float32)
            emb_norm = np.linalg.norm(emb)
            if emb_norm > 0:
                emb = emb / emb_norm
            cand_embeds.append(emb)

        cand_embeds = np.vstack(cand_embeds)  # Shape (N, D)

        # Calculate cosine similarities to the query: Shape (N,)
        query_similarities = np.dot(cand_embeds, q)

        selected_indices = []
        unselected_indices = list(range(len(valid_chunks)))

        # Select first chunk (highest similarity to the query)
        first_idx = int(np.argmax(query_similarities))
        selected_indices.append(first_idx)
        unselected_indices.remove(first_idx)

        # Pre-allocate matrix representing similarity of each candidate to selected candidates
        similarity_to_selected = np.zeros(
            (len(valid_chunks), top_k), dtype=np.float32
        )
        similarity_to_selected[:, 0] = np.dot(cand_embeds, cand_embeds[first_idx])

        while len(selected_indices) < min(top_k, len(valid_chunks)):
            best_mmr = -float("inf")
            best_idx = -1

            for i in unselected_indices:
                # Max similarity to any of the currently selected items
                max_selected_sim = np.max(
                    similarity_to_selected[i, : len(selected_indices)]
                )

                mmr_score = (
                    lambda_val * query_similarities[i]
                    - (1.0 - lambda_val) * max_selected_sim
                )
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_idx = i

            if best_idx == -1:
                break

            selected_indices.append(best_idx)
            unselected_indices.remove(best_idx)

            # Update similarity matrix for the newly selected item
            similarity_to_selected[:, len(selected_indices) - 1] = np.dot(
                cand_embeds, cand_embeds[best_idx]
            )

        return [valid_chunks[idx] for idx in selected_indices]
