from sqlalchemy.orm import Session

from app.database.enums import UserStatus
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.auth.register import (
    RegisterRequest,
    RegisterResponse,
)
from app.security.password_hasher import PasswordHasher

from app.exceptions.auth import EmailAlreadyExistsError

class AuthService:
    
    def __init__(self, db: Session):
        self.db = db

        self.users = UserRepository(db)
        self.workspaces = WorkspaceRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(self,request: RegisterRequest,) -> RegisterResponse:
        
        if self.users.exists_by_email(request.email):
            raise EmailAlreadyExistsError(
                "Email already registered."
            )

        password_hash = PasswordHasher.hash(request.password)

        user = User(email=request.email, full_name=request.full_name, password_hash=password_hash, status=UserStatus.PENDING_VERIFICATION, is_verified=False,)

        workspace = Workspace( owner=user, name="My Workspace",)

        try:
            self.users.add(user)

            self.workspaces.add(workspace)

            self.db.commit()

            self.db.refresh(user)

        except Exception:
            self.db.rollback()
            raise

        return RegisterResponse(
            message="Registration successful. Please verify your email."
        )