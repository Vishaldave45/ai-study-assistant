from __future__ import annotations


class StorageError(Exception):
    """Base exception for storage operations."""


class FileSaveError(StorageError):
    """Raised when a file cannot be saved."""


class FileDeleteError(StorageError):
    """Raised when a file cannot be deleted."""


class FileNotFoundError(StorageError):
    """Raised when a file cannot be found."""