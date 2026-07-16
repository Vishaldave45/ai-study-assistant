from app.core.config import settings, BASE_DIR

VECTOR_DIMENSION = 384
INDEX_TYPE = "FlatIP"
NORMALIZE = True

STORAGE_DIR = BASE_DIR / settings.STORAGE_DIRECTORY / "vectors"
