from fastapi import status


class BaseHTTPException(Exception):
    def __init__(
            self,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str = "Internal Server Error",
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)