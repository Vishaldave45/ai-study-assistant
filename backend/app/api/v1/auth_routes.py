
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    TokenResponse,
    LogoutRequest,
    LogoutResponse,
)


from app.services.auth_service import AuthService

from app.exceptions.auth import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccountNotVerifiedError,
    AccountSuspendedError,
)

from app.dependencies.auth import get_current_user
from app.database.models.user import User

router = APIRouter(prefix="/auth",tags=["Authentication"],)


@router.post("/register",response_model=RegisterResponse, status_code=status.HTTP_201_CREATED,)
def register(request: RegisterRequest,  db: Session = Depends(get_db),) -> RegisterResponse:

    service = AuthService(db)

    try:
        return service.register(request)

    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc),) from exc



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    print("=" * 50)
    print(request)
    print(type(request))
    service = AuthService(db)

    try:
        return service.login(
            request=request,
            ip_address=http_request.client.host
            if http_request.client
            else None,
            user_agent=http_request.headers.get("User-Agent"),
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except AccountNotVerifiedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except AccountSuspendedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh(
    request: RefreshTokenRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:

    service = AuthService(db)

    try:
        return service.refresh(
            request=request,
            ip_address=http_request.client.host
            if http_request.client
            else None,
            user_agent=http_request.headers.get(
                "User-Agent"
            ),
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except AccountSuspendedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    service.logout(
        request.refresh_token
    )

    return LogoutResponse(
        message="Logged out successfully."
    )
    
    
    
@router.get(
    "/me",
)
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "status": current_user.status.value,
        "verified": current_user.is_verified,
    }