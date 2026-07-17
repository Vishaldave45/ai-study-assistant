import logging
import pickle
from pathlib import Path
from uuid import UUID

logger = logging.getLogger(__name__)


class MetadataStore:

    def __init__(self, workspace_dir: Path):
        self.filepath = workspace_dir / "metadata.pkl"
        self.metadata = {}

    def load(self) -> dict:
        if self.filepath.exists():
            try:
                with open(self.filepath, "rb") as f:
                    self.metadata = pickle.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata file at {self.filepath}: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
        return self.metadata

    def save(self) -> None:
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "wb") as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Failed to save metadata file at {self.filepath}: {e}")
            raise

    def add_mappings(self, mappings: dict[int, dict]) -> None:
        self.metadata.update(mappings)

    def remove_by_document(self, document_id: UUID) -> list[int]:
        """
        Remove all metadata mappings associated with a specific document ID.
        Returns a list of vector IDs that were removed so they can be deleted from FAISS.
        """
        vector_ids_to_remove = []
        doc_id_str = str(document_id)

        for vector_id, meta in list(self.metadata.items()):
            if str(meta.get("document_id")) == doc_id_str:
                vector_ids_to_remove.append(vector_id)
                del self.metadata[vector_id]

        return vector_ids_to_remove

    def get_mapping(self, vector_id: int) -> dict | None:
        return self.metadata.get(vector_id)
