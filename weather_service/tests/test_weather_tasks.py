import json
from unittest.mock import Mock

from app.tasks.weather_tasks import update_weather_cache


def test_update_weather_cache_fetches_weather_and_saves_it(monkeypatch):
    weather_payload = {"current_condition": [{"temp_C": "19"}]}
    response_mock = Mock()
    response_mock.json.return_value = weather_payload
    response_mock.raise_for_status.return_value = None

    requests_get_mock = Mock(return_value=response_mock)
    redis_client_mock = Mock()
    redis_factory_mock = Mock(return_value=redis_client_mock)

    monkeypatch.setattr("app.tasks.weather_tasks.requests.get", requests_get_mock)
    monkeypatch.setattr("app.tasks.weather_tasks.redis.Redis", redis_factory_mock)

    result = update_weather_cache("Moscow")

    assert result == {
        "status": "updated",
        "city": "Moscow",
    }
    requests_get_mock.assert_called_once_with("http://wttr.in/Moscow?format=j1", timeout=10)
    redis_client_mock.set.assert_called_once_with(
        "Moscow",
        json.dumps(weather_payload),
        ex=3600,
    )
