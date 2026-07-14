from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

from app.services.auth_service import (AuthService,EmailAlreadyExistsError,)

router = APIRouter(prefix="/auth",tags=["Authentication"],)


@router.post("/register",response_model=RegisterResponse, status_code=status.HTTP_201_CREATED,)
def register(request: RegisterRequest,  db: Session = Depends(get_db),) -> RegisterResponse:

    service = AuthService(db)

    try:
        return service.register(request)

    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc),) from exc