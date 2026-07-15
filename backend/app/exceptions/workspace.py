class WorkspaceError(Exception):
    """Base workspace exception."""


class WorkspaceAlreadyExistsError(WorkspaceError):
    """Workspace already exists with the same name for this owner."""


class WorkspaceNotFoundError(WorkspaceError):
    """Workspace not found."""


class WorkspaceAccessDeniedError(WorkspaceError):
    """Access denied for this workspace."""
