from app.exceptions.weather_errors import (
    WeatherCacheDataMissingError,
    WeatherCacheUpdateTimeoutError,
)


def test_weather_cache_update_timeout_error_contains_expected_status_and_message():
    error = WeatherCacheUpdateTimeoutError(timeout_seconds=30)

    assert error.status_code == 504
    assert error.detail == "Кеш не обновлён за 30 секунд."


def test_weather_cache_data_missing_error_contains_expected_status_and_message():
    error = WeatherCacheDataMissingError()

    assert error.status_code == 500
    assert error.detail == "Задача обновления кеша завершилась, но данные не найдены в Redis."
