import numpy as np


def normalize_vectors(vectors: list[list[float]] | np.ndarray) -> np.ndarray:
    """
    Normalize vectors to unit length (L2 norm) to implement cosine similarity
    when using the Inner Product (FlatIP) FAISS index.
    """
    if isinstance(vectors, list):
        arr = np.array(vectors, dtype=np.float32)
    else:
        arr = vectors.astype(np.float32)

    if arr.ndim == 1:
        norm = np.linalg.norm(arr)
        if norm == 0:
            return arr
        return arr / norm
    else:
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        return arr / norms
