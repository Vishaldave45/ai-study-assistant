from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema
from app.security.token_types import TokenType


class TokenPayload(BaseSchema):
    sub: UUID
    jti: UUID
    iat: datetime
    exp: datetime
    type: TokenType