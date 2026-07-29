import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "AI Study Assistant"
    DEBUG: bool = True
    STORAGE_DIRECTORY: str = "storage"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024
    ALLOWED_MIME_TYPES: list[str] = [
        "application/pdf",
    ]

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "app" / ".env",
        case_sensitive=True,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Return latest Settings reading directly from app/.env."""
    return Settings(_env_file=BASE_DIR / "app" / ".env")


class DynamicSettings:
    """Proxy class that resolves settings dynamically."""
    def __getattr__(self, name: str):
        # Allow direct environment variable override (e.g. GEMINI_API_KEY)
        if name in os.environ:
            return os.environ[name]
        return getattr(get_settings(), name)


settings = DynamicSettings()
