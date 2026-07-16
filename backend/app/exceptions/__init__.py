from .auth import (
    AccountNotVerifiedError,
    AccountSuspendedError,
    AuthError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from .workspace import (
    WorkspaceError,
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
    WorkspaceAccessDeniedError,
)
from .document import (
    DocumentError,
    DocumentNotFoundError,
    DocumentAccessDeniedError,
    InvalidFileTypeError,
    FileSizeExceededError,
)

__all__ = [
    "AuthError",
    "EmailAlreadyExistsError",
    "InvalidCredentialsError",
    "AccountNotVerifiedError",
    "AccountSuspendedError",
    "WorkspaceError",
    "WorkspaceAlreadyExistsError",
    "WorkspaceNotFoundError",
    "WorkspaceAccessDeniedError",
    "DocumentError",
    "DocumentNotFoundError",
    "DocumentAccessDeniedError",
    "InvalidFileTypeError",
    "FileSizeExceededError",
]
