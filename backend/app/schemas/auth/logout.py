from pydantic import Field

from app.schemas.base import BaseSchema


class LogoutRequest(BaseSchema):
    refresh_token: str = Field(
        min_length=32,
    )


class LogoutResponse(BaseSchema):
    message: str
