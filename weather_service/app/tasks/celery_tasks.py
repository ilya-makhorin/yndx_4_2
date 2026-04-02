from celery import Celery

from app.config import settings

celery_app = Celery(
    "weather_tasks",
    broker=(
        f"amqp://{settings.RABBITMQ_DEFAULT_USER}:"
        f"{settings.RABBITMQ_DEFAULT_PASS}@"
        f"{settings.rabbitmq_host}:{settings.rabbitmq_port}//"
    ),
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)

celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "update-moscow-weather-every-10-min": {
        "task": "app.tasks.weather_tasks.update_weather_cache",
        "schedule": 600.0,
        "args": ("moscow",),
    },
    "update-dubai-weather-every-10-min": {
        "task": "app.tasks.weather_tasks.update_weather_cache",
        "schedule": 600.0,
        "args": ("dubai",),
    },
}

from app.tasks import weather_tasks  # noqa: E402,F401

