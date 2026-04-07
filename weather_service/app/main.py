from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.endpoints import router as weather_router
from app.api.weather_ws import router as weather_ws_router
from app.db import Base, engine
from app.exceptions.handlers import register_exception_handlers
from app import models  # noqa: F401


app = FastAPI(title="Weather Service")

app.include_router(auth_router)
app.include_router(weather_router)
app.include_router(weather_ws_router)
register_exception_handlers(app)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
