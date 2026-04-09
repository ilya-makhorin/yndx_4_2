import os
import sys
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault("redis_host", "localhost")
os.environ.setdefault("redis_port", "6379")
os.environ.setdefault("rabbitmq_host", "localhost")
os.environ.setdefault("rabbitmq_port", "5672")
os.environ.setdefault("rabbitmq_management_port", "15672")
os.environ.setdefault("app_port", "8000")
os.environ.setdefault("RABBITMQ_DEFAULT_USER", "guest")
os.environ.setdefault("RABBITMQ_DEFAULT_PASS", "guest")
os.environ.setdefault("postgres_host", "localhost")
os.environ.setdefault("postgres_port", "5432")
os.environ.setdefault("postgres_db", "test_db")
os.environ.setdefault("postgres_user", "test_user")
os.environ.setdefault("postgres_password", "test_password")
os.environ.setdefault("jwt_secret_key", "test-secret")
os.environ.setdefault("jwt_algorithm", "HS256")
os.environ.setdefault("jwt_access_token_expire_minutes", "60")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth import router as auth_router
from app.api.endpoints import router as weather_router
from app.api.weather_ws import router as weather_ws_router
from app.dependencies import get_auth_usecase, get_current_user
from app.exceptions.handlers import register_exception_handlers
from app.models import User


class InMemoryAuthUseCase:
    def __init__(self) -> None:
        self.register_response = None
        self.login_response = None

    def register_user(self, email: str, password: str):
        if callable(self.register_response):
            return self.register_response(email, password)
        return self.register_response

    def login_user(self, email: str, password: str):
        if callable(self.login_response):
            return self.login_response(email, password)
        return self.login_response


@pytest.fixture
def sample_user() -> User:
    user = User(
        id=1,
        email="user@example.com",
        hashed_password="hashed",
    )
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def auth_usecase_stub() -> InMemoryAuthUseCase:
    stub = InMemoryAuthUseCase()
    stub.register_response = None
    stub.login_response = "test-token"
    return stub


@pytest.fixture
def test_app(sample_user: User, auth_usecase_stub: InMemoryAuthUseCase) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(weather_router)
    app.include_router(weather_ws_router)
    register_exception_handlers(app)

    app.dependency_overrides[get_auth_usecase] = lambda: auth_usecase_stub
    app.dependency_overrides[get_current_user] = lambda: sample_user
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    with TestClient(test_app) as test_client:
        yield test_client
