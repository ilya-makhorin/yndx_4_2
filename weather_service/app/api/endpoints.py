from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.usecases.weather_usecase import get_city_weather_with_event_uc

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/{city}")
async def get_city_weather(city: str, _: User = Depends(get_current_user)):
    return await get_city_weather_with_event_uc(city)
