class AuthError(Exception):
    """Base authentication exception."""


class EmailAlreadyExistsError(AuthError):
    """Email already exists."""


class InvalidCredentialsError(AuthError):
    """Invalid email or password."""


class AccountNotVerifiedError(AuthError):
    """Email not verified."""


class AccountSuspendedError(AuthError):
    """Account suspended."""