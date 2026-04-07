import anyio
from celery.exceptions import TimeoutError

from app.exceptions.weather_errors import (
    WeatherCacheDataMissingError,
    WeatherCacheUpdateTimeoutError,
)
from app.services.weather_service import get_weather
from app.tasks.weather_tasks import update_weather_cache

from app.services.websocket_manager import weather_ws_manager


async def get_city_weather_uc(city: str, timeout_seconds: int = 1500) -> dict:

    cached = await get_weather(city)
    if cached is not None:
        return cached

    async_result = update_weather_cache.delay(city)

    try:
        await anyio.to_thread.run_sync(
            lambda: async_result.get(timeout=timeout_seconds)
        )
    except TimeoutError as exc:
        raise WeatherCacheUpdateTimeoutError(timeout_seconds) from exc

    cached_after = await get_weather(city)
    if cached_after is None:
        raise WeatherCacheDataMissingError()

    return cached_after


async def get_city_weather_with_event_uc(city: str) -> dict:
    data = await get_city_weather_uc(city)

    current_condition = data.get("current_condition", [])
    temperature_c = None

    if current_condition:
        temperature_c = current_condition[0].get("temp_C")

    await weather_ws_manager.broadcast_json(
        {
            "city": city,
            "temperature_c": temperature_c,
        }
    )

    return {
        "source": "cache",
        "status": "ok",
        "city": city,
        "data": data,
    }
