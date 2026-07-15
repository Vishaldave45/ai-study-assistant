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
    TokenResponse,
)


from app.services.auth_service import AuthService

from app.exceptions.auth import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccountNotVerifiedError,
    AccountSuspendedError,
)

router = APIRouter(prefix="/auth",tags=["Authentication"],)


@router.post("/register",response_model=RegisterResponse, status_code=status.HTTP_201_CREATED,)
def register(request: RegisterRequest,  db: Session = Depends(get_db),) -> RegisterResponse:

    service = AuthService(db)

    try:
        return service.register(request)

    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc),) from exc



@router.post("/login", response_model=TokenResponse, status_code= status.HTTP_200_OK)
def login(Request:LoginRequest , http_request: Request, db: Session=Depends(get_db) , )->TokenResponse:
    service=AuthService(db)
    

    try:
        
        return service.login(
                request=LoginRequest,
                ip_address=http_request.client.host
                if http_request.client
                else None,
                user_agent=http_request.headers.get(
                    "User-Agent"
                ),
        )

    except InvalidCredentialsError as EXC:
        raise HTTPException( status_code = status.HTTP_401_UNAUTHORIZED, detail=str(EXC),) from exc

    except AccountNotVerifiedError as exc:
        raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, detail=str(exc),) from exc

    except AccountSuspendedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc), ) from exc
    
    