from unittest.mock import AsyncMock

import pytest
from starlette.websockets import WebSocketDisconnect

from app.exceptions.weather_errors import WeatherCacheUpdateTimeoutError
from app.models import User


def test_register_user_returns_created_user(client, auth_usecase_stub, sample_user: User):
    auth_usecase_stub.register_response = sample_user

    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "email": "user@example.com",
        "created_at": "2024-01-01T00:00:00Z",
    }


def test_login_user_returns_access_token(client, auth_usecase_stub):
    auth_usecase_stub.login_response = "jwt-token"

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "jwt-token",
        "token_type": "bearer",
    }


def test_weather_endpoint_returns_usecase_payload(client, monkeypatch):
    payload = {
        "source": "cache",
        "status": "ok",
        "city": "Moscow",
        "data": {"current_condition": [{"temp_C": "7"}]},
    }

    monkeypatch.setattr(
        "app.api.endpoints.get_city_weather_with_event_uc",
        AsyncMock(return_value=payload),
    )

    response = client.get("/weather/Moscow")

    assert response.status_code == 200
    assert response.json() == payload


def test_weather_endpoint_uses_registered_exception_handler(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.endpoints.get_city_weather_with_event_uc",
        AsyncMock(side_effect=WeatherCacheUpdateTimeoutError(5)),
    )

    response = client.get("/weather/Moscow")

    assert response.status_code == 504
    assert response.json() == {"detail": "Кеш не обновлён за 5 секунд."}


def test_websocket_rejects_invalid_token(client, monkeypatch):
    monkeypatch.setattr("app.api.weather_ws.decode_access_token", lambda token: (_ for _ in ()).throw(ValueError("bad token")))

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/weather?token=bad-token"):
            pass

    assert exc_info.value.code == 1008
    assert exc_info.value.reason == "Невалидный токен."
