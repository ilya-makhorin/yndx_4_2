from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import weather_ws_manager
from app.services.security import decode_access_token

router = APIRouter()


@router.websocket("/ws/weather")
async def websocket_weather(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Требуется токен.")
        return

    try:
        decode_access_token(token)
    except ValueError:
        await websocket.close(code=1008, reason="Невалидный токен.")
        return

    await weather_ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        weather_ws_manager.disconnect(websocket)
