from app.storage.local_storage import LocalStorageProvider

# Alias LocalStorageProvider to LocalStorage as requested
LocalStorage = LocalStorageProvider

# Instantiate and expose the storage singleton
storage = LocalStorage()

__all__ = [
    "LocalStorage",
    "storage",
]
