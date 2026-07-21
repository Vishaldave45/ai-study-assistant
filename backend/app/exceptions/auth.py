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


class UserNotFoundError(AuthError):
    """User not found."""


class InvalidResetTokenError(AuthError):
    """Invalid or expired reset token."""
