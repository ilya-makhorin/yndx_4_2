from fastapi import status

from app.exceptions.base import BaseHTTPException


class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Пользователь с таким email уже существует",
        )


class InvalidCredentialsError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )


class InvalidOrExpiredTokenError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
        )


class UserNotFoundError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
