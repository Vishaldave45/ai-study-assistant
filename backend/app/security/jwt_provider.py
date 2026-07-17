from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as PyJWTInvalidTokenError

from app.core.config import settings
from app.security.exceptions import ExpiredTokenError, InvalidTokenError
from app.security.token_types import TokenType

if TYPE_CHECKING:
    from app.schemas.auth.token_payload import TokenPayload


class JWTProvider:
    ALGORITHM = "HS256"

    @classmethod
    def create_access_token(
        cls,
        user_id: UUID,
    ) -> str:

        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": str(uuid4()),
            "type": TokenType.ACCESS.value,
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

    @classmethod
    def verify(
        cls,
        token: str,
    ) -> TokenPayload:
        from app.schemas.auth.token_payload import TokenPayload

        try:

            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[cls.ALGORITHM],
            )

            return TokenPayload.model_validate(payload)

        except ExpiredSignatureError as exc:
            raise ExpiredTokenError from exc

        except PyJWTInvalidTokenError as exc:
            raise InvalidTokenError from exc
