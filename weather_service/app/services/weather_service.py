import json

import redis.asyncio as redis

from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


async def get_weather(city: str) -> dict | None:
    raw = await redis_client.get(city)
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        return raw

