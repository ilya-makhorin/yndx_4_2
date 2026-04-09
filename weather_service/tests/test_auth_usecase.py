from unittest.mock import Mock

import pytest

from app.exceptions.auth_errors import InvalidCredentialsError, UserAlreadyExistsError
from app.models import User
from app.usecases.auth_usecase import AuthUseCase


def test_register_user_hashes_password_and_creates_user(monkeypatch):
    repository = Mock()
    repository.get_by_email.return_value = None
    created_user = User(id=7, email="new@example.com", hashed_password="hashed-value")
    repository.create.return_value = created_user

    monkeypatch.setattr("app.usecases.auth_usecase.hash_password", lambda password: f"hashed::{password}")

    usecase = AuthUseCase(repository)

    result = usecase.register_user("new@example.com", "plain-password")

    assert result is created_user
    repository.get_by_email.assert_called_once_with("new@example.com")
    repository.create.assert_called_once_with(
        email="new@example.com",
        hashed_password="hashed::plain-password",
    )


def test_register_user_raises_when_email_already_exists():
    repository = Mock()
    repository.get_by_email.return_value = User(id=1, email="taken@example.com", hashed_password="hashed")
    usecase = AuthUseCase(repository)

    with pytest.raises(UserAlreadyExistsError):
        usecase.register_user("taken@example.com", "password123")

    repository.create.assert_not_called()


def test_login_user_returns_token_for_valid_credentials(monkeypatch):
    repository = Mock()
    repository.get_by_email.return_value = User(id=3, email="user@example.com", hashed_password="stored-hash")

    monkeypatch.setattr("app.usecases.auth_usecase.verify_password", lambda plain, hashed: plain == "secret123" and hashed == "stored-hash")
    monkeypatch.setattr("app.usecases.auth_usecase.create_access_token", lambda user_id: f"token-for-{user_id}")

    usecase = AuthUseCase(repository)

    result = usecase.login_user("user@example.com", "secret123")

    assert result == "token-for-3"


def test_login_user_raises_for_unknown_user():
    repository = Mock()
    repository.get_by_email.return_value = None
    usecase = AuthUseCase(repository)

    with pytest.raises(InvalidCredentialsError):
        usecase.login_user("missing@example.com", "secret123")


def test_login_user_raises_for_invalid_password(monkeypatch):
    repository = Mock()
    repository.get_by_email.return_value = User(id=3, email="user@example.com", hashed_password="stored-hash")

    monkeypatch.setattr("app.usecases.auth_usecase.verify_password", lambda *_: False)

    usecase = AuthUseCase(repository)

    with pytest.raises(InvalidCredentialsError):
        usecase.login_user("user@example.com", "wrong-password")
