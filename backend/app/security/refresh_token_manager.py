from __future__ import annotations

import hashlib
import secrets
from hmac import compare_digest


class RefreshTokenManager:
    TOKEN_BYTES = 64

    @classmethod
    def generate(cls) -> str:
        return secrets.token_urlsafe(cls.TOKEN_BYTES)

    @classmethod
    def hash(cls, token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    @classmethod
    def verify(
        cls,
        token: str,
        token_hash: str,
    ) -> bool:
        return compare_digest(
            cls.hash(token),
            token_hash,
        )