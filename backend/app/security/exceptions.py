class InvalidTokenError(Exception):
    """Raised when a JWT is invalid."""


class ExpiredTokenError(Exception):
    """Raised when a JWT has expired."""