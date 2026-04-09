from unittest.mock import AsyncMock, Mock

import pytest
from celery.exceptions import TimeoutError

from app.exceptions.weather_errors import (
    WeatherCacheDataMissingError,
    WeatherCacheUpdateTimeoutError,
)
from app.usecases.weather_usecase import (
    get_city_weather_uc,
    get_city_weather_with_event_uc,
)


@pytest.mark.asyncio
async def test_get_city_weather_uc_returns_cached_value_without_updating(monkeypatch):
    cached = {"current_condition": [{"temp_C": "12"}]}
    delay_mock = Mock()

    monkeypatch.setattr("app.usecases.weather_usecase.get_weather", AsyncMock(return_value=cached))
    monkeypatch.setattr("app.usecases.weather_usecase.update_weather_cache", Mock(delay=delay_mock))

    result = await get_city_weather_uc("Moscow")

    assert result == cached
    delay_mock.assert_not_called()


@pytest.mark.asyncio
async def test_get_city_weather_uc_raises_timeout_when_task_takes_too_long(monkeypatch):
    async_result = Mock()
    async_result.get.side_effect = TimeoutError("task timeout")

    monkeypatch.setattr("app.usecases.weather_usecase.get_weather", AsyncMock(return_value=None))
    monkeypatch.setattr("app.usecases.weather_usecase.update_weather_cache", Mock(delay=Mock(return_value=async_result)))

    with pytest.raises(WeatherCacheUpdateTimeoutError) as exc_info:
        await get_city_weather_uc("Moscow", timeout_seconds=15)

    assert exc_info.value.status_code == 504
    assert exc_info.value.detail == "Кеш не обновлён за 15 секунд."


@pytest.mark.asyncio
async def test_get_city_weather_uc_raises_when_cache_still_missing_after_refresh(monkeypatch):
    async_result = Mock()
    async_result.get.return_value = {"status": "updated"}
    get_weather_mock = AsyncMock(side_effect=[None, None])

    monkeypatch.setattr("app.usecases.weather_usecase.get_weather", get_weather_mock)
    monkeypatch.setattr("app.usecases.weather_usecase.update_weather_cache", Mock(delay=Mock(return_value=async_result)))

    with pytest.raises(WeatherCacheDataMissingError):
        await get_city_weather_uc("Moscow")

    assert get_weather_mock.await_count == 2


@pytest.mark.asyncio
async def test_get_city_weather_uc_returns_value_after_background_refresh(monkeypatch):
    refreshed = {"current_condition": [{"temp_C": "18"}]}
    async_result = Mock()
    async_result.get.return_value = {"status": "updated"}
    get_weather_mock = AsyncMock(side_effect=[None, refreshed])

    monkeypatch.setattr("app.usecases.weather_usecase.get_weather", get_weather_mock)
    monkeypatch.setattr("app.usecases.weather_usecase.update_weather_cache", Mock(delay=Mock(return_value=async_result)))

    result = await get_city_weather_uc("Moscow")

    assert result == refreshed


@pytest.mark.asyncio
async def test_get_city_weather_with_event_uc_broadcasts_temperature(monkeypatch):
    weather_payload = {"current_condition": [{"temp_C": "24"}]}
    broadcast_mock = AsyncMock()

    monkeypatch.setattr("app.usecases.weather_usecase.get_city_weather_uc", AsyncMock(return_value=weather_payload))
    monkeypatch.setattr("app.usecases.weather_usecase.weather_ws_manager.broadcast_json", broadcast_mock)

    result = await get_city_weather_with_event_uc("Dubai")

    assert result == {
        "source": "cache",
        "status": "ok",
        "city": "Dubai",
        "data": weather_payload,
    }
    broadcast_mock.assert_awaited_once_with(
        {
            "city": "Dubai",
            "temperature_c": "24",
        }
    )
