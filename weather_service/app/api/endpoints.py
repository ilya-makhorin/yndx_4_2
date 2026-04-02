from fastapi import APIRouter
from app.usecases.weather_usecase import get_city_weather_with_event_uc

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/{city}")
async def get_city_weather(city: str):
    return await get_city_weather_with_event_uc(city)