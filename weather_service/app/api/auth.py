from fastapi import APIRouter, Depends, status
from app.dependencies import get_auth_usecase
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.usecases.auth_usecase import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    return auth_usecase.register_user(payload.email, payload.password)


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
) -> TokenResponse:
    access_token = auth_usecase.login_user(payload.email, payload.password)
    return TokenResponse(access_token=access_token)
