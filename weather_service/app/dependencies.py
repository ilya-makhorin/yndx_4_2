from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions.auth_errors import (
    InvalidOrExpiredTokenError,
    UserNotFoundError,
)
from app.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.repositories.user_repository import UserRepository
from app.services.security import decode_access_token
from app.usecases.auth_usecase import AuthUseCase

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepository(db)


def get_auth_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthUseCase:
    return AuthUseCase(user_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
):
    if credentials is None:
        raise InvalidOrExpiredTokenError()

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
    except (ValueError, TypeError):
        raise InvalidOrExpiredTokenError()

    user = user_repository.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    return user
