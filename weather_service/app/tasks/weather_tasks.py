import json

import redis
import requests

from app.config import settings
from app.tasks.celery_tasks import celery_app


@celery_app.task(name="app.tasks.weather_tasks.update_weather_cache")
def update_weather_cache(city: str) -> dict:

    url = f"http://wttr.in/{city}?format=j1"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    weather_data = resp.json()

    r = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )
    r.set(city, json.dumps(weather_data), ex=3600)

    return {
        "status": "updated",
        "city": city,
    }