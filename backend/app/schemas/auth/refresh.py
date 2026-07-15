from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.auth.login import TokenResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str = Field(
        min_length=32,
    )


__all__ = [
    "RefreshTokenRequest",
    "TokenResponse",
]
