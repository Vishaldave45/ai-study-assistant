from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.session import engine
from app.database.base import Base
import app.database.models  # noqa: F401

# Create tables if they do not exist
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def health():
    return {"status": "ok"}
