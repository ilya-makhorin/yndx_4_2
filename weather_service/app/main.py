from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.endpoints import router as weather_router
from app.api.weather_ws import router as weather_ws_router


app = FastAPI(title="Weather Service")

app.include_router(weather_router)
app.include_router(weather_ws_router)

@app.exception_handler(Exception)
async def cache_timeout_handler(_, __):
    return JSONResponse(
        status_code=504,
        content={
            "detail": "Не удалось получить данные погоды: таймаут обновления кеша."
        },
    )


@app.exception_handler(Exception)
async def cache_missing_handler(_, __):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Задача обновления кеша завершилась, но данные не найдены в Redis."
        },
    )