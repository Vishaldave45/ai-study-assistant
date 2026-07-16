import logging
from pathlib import Path
from uuid import UUID
import faiss
import numpy as np

from app.vectorstore.config import NORMALIZE, STORAGE_DIR, VECTOR_DIMENSION
from app.vectorstore.exceptions import (
    DimensionMismatchError,
    IndexNotFoundError,
    SearchError,
    VectorStoreError,
)
from app.vectorstore.metadata_store import MetadataStore
from app.vectorstore.provider import VectorStoreProvider
from app.vectorstore.schemas import SearchResult
from app.vectorstore.utils import normalize_vectors

logger = logging.getLogger(__name__)


class FAISSVectorStore(VectorStoreProvider):

    def __init__(self):
        self.storage_dir = Path(STORAGE_DIR)
        # Cache of loaded indexes and metadata stores in memory
        # {workspace_id: (faiss_index, metadata_store)}
        self._cache = {}

    def _get_workspace_paths(self, workspace_id: UUID) -> tuple[Path, Path, Path]:
        workspace_dir = self.storage_dir / str(workspace_id)
        index_path = workspace_dir / "index.faiss"
        metadata_path = workspace_dir / "metadata.pkl"
        return workspace_dir, index_path, metadata_path

    def create(self, workspace_id: UUID) -> None:
        workspace_dir, index_path, metadata_path = self._get_workspace_paths(workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Create empty IndexFlatIP wrapped in IndexIDMap
        sub_index = faiss.IndexFlatIP(VECTOR_DIMENSION)
        index = faiss.IndexIDMap(sub_index)

        metadata_store = MetadataStore(workspace_dir)
        metadata_store.metadata = {}

        self._cache[workspace_id] = (index, metadata_store)
        logger.info(f"Created new empty FAISS index for workspace {workspace_id}")

    def load(self, workspace_id: UUID) -> None:
        workspace_dir, index_path, metadata_path = self._get_workspace_paths(workspace_id)

        if not index_path.exists() or not metadata_path.exists():
            raise IndexNotFoundError(f"Index or metadata not found for workspace {workspace_id}")

        try:
            index = faiss.read_index(str(index_path))
            metadata_store = MetadataStore(workspace_dir)
            metadata_store.load()
            self._cache[workspace_id] = (index, metadata_store)
            logger.info(f"Loaded FAISS index for workspace {workspace_id} from disk")
        except Exception as e:
            logger.error(f"Failed to load FAISS index for workspace {workspace_id}: {e}")
            raise IndexNotFoundError(f"Failed to load FAISS index for workspace {workspace_id}: {e}") from e

    def save(self, workspace_id: UUID) -> None:
        if workspace_id not in self._cache:
            raise IndexNotFoundError(f"Workspace {workspace_id} is not loaded in memory.")

        workspace_dir, index_path, metadata_path = self._get_workspace_paths(workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        index, metadata_store = self._cache[workspace_id]
        try:
            faiss.write_index(index, str(index_path))
            metadata_store.save()
            logger.info(f"Saved FAISS index and metadata for workspace {workspace_id} to disk")
        except Exception as e:
            logger.error(f"Failed to save FAISS index for workspace {workspace_id}: {e}")
            raise VectorStoreError(f"Failed to save FAISS index: {e}") from e

    def _ensure_loaded(self, workspace_id: UUID) -> tuple[faiss.Index, MetadataStore]:
        if workspace_id not in self._cache:
            try:
                self.load(workspace_id)
            except IndexNotFoundError:
                # If it doesn't exist on disk, create a new one
                self.create(workspace_id)
        return self._cache[workspace_id]

    def add(
        self,
        workspace_id: UUID,
        vectors: list[list[float]],
        metadata: list[dict],
    ) -> None:
        if not vectors:
            return

        index, metadata_store = self._ensure_loaded(workspace_id)

        # Validate dimensions
        for v in vectors:
            if len(v) != VECTOR_DIMENSION:
                raise DimensionMismatchError(
                    f"Vector dimension {len(v)} does not match index dimension {VECTOR_DIMENSION}"
                )

        # Normalize vectors if configured
        if NORMALIZE:
            vectors_np = normalize_vectors(vectors)
        else:
            vectors_np = np.array(vectors, dtype=np.float32)

        # Determine next ID to use
        if metadata_store.metadata:
            next_id = max(metadata_store.metadata.keys()) + 1
        else:
            next_id = 0

        ids = list(range(next_id, next_id + len(vectors)))
        ids_np = np.array(ids, dtype=np.int64)

        # Add to FAISS index
        index.add_with_ids(vectors_np, ids_np)

        # Add to metadata store
        new_mappings = {}
        for idx, meta in zip(ids, metadata):
            new_mappings[idx] = {
                "chunk_id": meta["chunk_id"],
                "document_id": meta["document_id"],
                "workspace_id": workspace_id,
            }
        metadata_store.add_mappings(new_mappings)
        logger.info(f"Added {len(vectors)} vectors to workspace {workspace_id} index.")

    def search(
        self,
        workspace_id: UUID,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        if len(query_vector) != VECTOR_DIMENSION:
            raise DimensionMismatchError(
                f"Query vector dimension {len(query_vector)} does not match index dimension {VECTOR_DIMENSION}"
            )

        index, metadata_store = self._ensure_loaded(workspace_id)

        if index.ntotal == 0:
            return []

        # Normalize query vector
        if NORMALIZE:
            query_np = normalize_vectors([query_vector])
        else:
            query_np = np.array([query_vector], dtype=np.float32)

        try:
            # Search
            scores, indices = index.search(query_np, top_k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue  # FAISS returns -1 if not enough results
                meta = metadata_store.get_mapping(int(idx))
                if meta:
                    results.append(
                        SearchResult(
                            chunk_id=meta["chunk_id"],
                            score=float(score),
                            document_id=meta["document_id"],
                            workspace_id=meta["workspace_id"],
                        )
                    )
            return results
        except Exception as e:
            logger.error(f"Search failed for workspace {workspace_id}: {e}")
            raise SearchError(f"Search failed: {e}") from e

    def delete(self, workspace_id: UUID, document_id: UUID) -> None:
        index, metadata_store = self._ensure_loaded(workspace_id)

        # Remove from metadata and get vector IDs to remove from FAISS
        vector_ids_to_remove = metadata_store.remove_by_document(document_id)

        if vector_ids_to_remove:
            ids_np = np.array(vector_ids_to_remove, dtype=np.int64)
            index.remove_ids(ids_np)
            logger.info(
                f"Deleted {len(vector_ids_to_remove)} vectors for document {document_id} "
                f"from workspace {workspace_id} index."
            )

    def reset(self, workspace_id: UUID) -> None:
        index, metadata_store = self._ensure_loaded(workspace_id)
        index.reset()
        metadata_store.metadata = {}
        logger.info(f"Reset FAISS index and metadata for workspace {workspace_id}")

    def index_exists(self, workspace_id: UUID) -> bool:
        """
        Check if the index and metadata PKL file exist on disk for the workspace.
        """
        workspace_dir, index_path, metadata_path = self._get_workspace_paths(workspace_id)
        return index_path.exists() and metadata_path.exists()

