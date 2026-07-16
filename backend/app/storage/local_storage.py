import shutil
from io import BytesIO
from pathlib import Path
from app.storage.base import StorageProvider
from app.storage.exceptions import (
    StorageError,
    FileSaveError,
    FileDeleteError,
    FileNotFoundError,
)


class LocalStorageProvider(StorageProvider):
    """
    LocalStorageProvider implements StorageProvider using the local filesystem.
    """

    def __init__(self, base_path: str | Path | None = None):
        if base_path is None:
            # Default to 'storage' directory in project root
            self.base_path = Path(__file__).resolve().parent.parent.parent / "storage"
        else:
            self.base_path = Path(base_path)

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_absolute_path(self, path: str) -> Path:
        """
        Resolve a path against the base path and prevent directory traversal.
        """
        # Clean path and resolve absolute path
        cleaned_path = Path(path.lstrip("/"))
        abs_path = (self.base_path / cleaned_path).resolve()

        # Verify it doesn't escape base_path
        if not abs_path.is_relative_to(self.base_path.resolve()):
            raise FileNotFoundError(
                f"Path '{path}' is invalid or outside storage root."
            )

        return abs_path

    def save(self, path: str, data: BytesIO) -> bool:
        try:
            abs_path = self._get_absolute_path(path)
            abs_path.parent.mkdir(parents=True, exist_ok=True)

            # Reset buffer and write file
            data.seek(0)
            with open(abs_path, "wb") as f:
                shutil.copyfileobj(data, f)
            return True
        except Exception as e:
            raise FileSaveError(f"Failed to save file to {path}: {str(e)}") from e

    def delete(self, path: str) -> bool:
        try:
            abs_path = self._get_absolute_path(path)
            if not abs_path.exists():
                return False
            if abs_path.is_dir():
                raise FileDeleteError(f"Path '{path}' is a directory, not a file.")
            abs_path.unlink()
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            raise FileDeleteError(f"Failed to delete file {path}: {str(e)}") from e

    def exists(self, path: str) -> bool:
        try:
            abs_path = self._get_absolute_path(path)
            return abs_path.exists() and abs_path.is_file()
        except FileNotFoundError:
            return False

    def open(self, path: str) -> BytesIO:
        try:
            abs_path = self._get_absolute_path(path)
            if not abs_path.exists() or not abs_path.is_file():
                raise FileNotFoundError(f"File {path} not found.")

            with open(abs_path, "rb") as f:
                return BytesIO(f.read())
        except FileNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to open file {path}: {str(e)}") from e

    def url(self, path: str) -> str:
        return str(Path(path.lstrip("/")))
