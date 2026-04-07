from fastapi import status

from app.exceptions.base import BaseHTTPException


class WeatherCacheUpdateTimeoutError(BaseHTTPException):
    def __init__(self, timeot_seconds: int) -> None:
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Кеш не обновлен за {timeot_seconds} секунд",
        )


class WeatherCacheDataMissingError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Задача обновления кеша завершилась, но данные не найдены",
        )
