from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.enums import UserStatus
from app.database.models.user import User
from app.database.models.workspace import Workspace
from app.database.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.auth.register import (
    RegisterRequest,
    RegisterResponse,
)
from app.schemas.auth.login import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.auth.refresh import RefreshTokenRequest
from app.schemas.auth.forgot_password import ForgotPasswordRequest
from app.schemas.auth.reset_password import ResetPasswordRequest

from app.security.password_hasher import PasswordHasher
from app.security.jwt_provider import JWTProvider
from app.security.refresh_token_manager import RefreshTokenManager
from app.security.token_types import TokenType
from app.security.exceptions import ExpiredTokenError, InvalidTokenError

from app.exceptions.auth import (
    AccountNotVerifiedError,
    AccountSuspendedError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    InvalidResetTokenError,
)


class AuthService:

    def __init__(self, db: Session):
        self.db = db

        self.users = UserRepository(db)
        self.workspaces = WorkspaceRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(
        self,
        request: RegisterRequest,
    ) -> RegisterResponse:

        if self.users.exists_by_email(request.email):
            raise EmailAlreadyExistsError("Email already registered.")

        password_hash = PasswordHasher.hash(request.password)

        user = User(
            email=request.email,
            full_name=request.full_name,
            password_hash=password_hash,
            status=UserStatus.PENDING_VERIFICATION,
            is_verified=False,
        )

        workspace = Workspace(
            owner=user,
            name="My Workspace",
        )

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

    def login(
        self,
        request: LoginRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:

        user = self.users.get_by_email(request.email)

        if user is None:
            raise InvalidCredentialsError("Invalid email or password.")

        if not PasswordHasher.verify(
            request.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError("Invalid email or password.")

        """if not user.is_verified:
            raise AccountNotVerifiedError("Please verify your email first.")"""

        if user.status == UserStatus.SUSPENDED:
            raise AccountSuspendedError("Your account has been suspended.")

        access_token = JWTProvider.create_access_token(
            user.id,
        )

        refresh_token = RefreshTokenManager.generate()

        refresh_token_hash = RefreshTokenManager.hash(
            refresh_token,
        )

        refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.refresh_tokens.add(refresh_entity)

        user.last_login_at = datetime.utcnow()

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
        )

    def refresh(
        self,
        request: RefreshTokenRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:

        token_hash = RefreshTokenManager.hash(request.refresh_token)

        refresh_entity = self.refresh_tokens.get_active_by_token_hash(token_hash)

        if refresh_entity is None:
            raise InvalidCredentialsError("Invalid refresh token.")

        if refresh_entity.expires_at < datetime.utcnow():
            raise InvalidCredentialsError("Refresh token expired.")

        user = refresh_entity.user

        if user.status == UserStatus.SUSPENDED:
            raise AccountSuspendedError("Your account has been suspended.")

        self.refresh_tokens.revoke(refresh_entity)

        access_token = JWTProvider.create_access_token(user.id)

        new_refresh_token = RefreshTokenManager.generate()

        new_refresh_hash = RefreshTokenManager.hash(new_refresh_token)

        refresh = RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_hash,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.refresh_tokens.add(refresh)

        user.last_login_at = datetime.utcnow()

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
        )

    def logout(
        self,
        refresh_token: str,
    ) -> None:

        token_hash = RefreshTokenManager.hash(refresh_token)

        token = self.refresh_tokens.get_active_by_token_hash(token_hash)

        if token is None:
            return

        self.refresh_tokens.revoke(token)

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def forgot_password(
        self,
        request: ForgotPasswordRequest,
    ) -> str:
        user = self.users.get_by_email(request.email)
        if user is None:
            raise UserNotFoundError("User with this email does not exist.")

        reset_token = JWTProvider.create_password_reset_token(user.id)

        print("\n" + "=" * 80)
        print(f" PASSWORD RESET REQUEST FOR EMAIL: {request.email}")
        print(f" RESET TOKEN: {reset_token}")
        print("=" * 80 + "\n")

        return reset_token

    def reset_password(
        self,
        request: ResetPasswordRequest,
    ) -> None:
        try:
            payload = JWTProvider.verify(request.token)
        except (ExpiredTokenError, InvalidTokenError) as exc:
            raise InvalidResetTokenError(
                "The password reset token is invalid or has expired."
            ) from exc

        if payload.type != TokenType.PASSWORD_RESET:
            raise InvalidResetTokenError("Invalid token type.")

        user = self.users.get_by_id(payload.sub)
        if user is None:
            raise UserNotFoundError("User not found.")

        user.password_hash = PasswordHasher.hash(request.password)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

