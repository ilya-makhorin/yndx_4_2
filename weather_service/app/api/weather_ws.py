from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import weather_ws_manager

router = APIRouter()


@router.websocket("/ws/weather")
async def websocket_weather(websocket: WebSocket) -> None:
    await weather_ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        weather_ws_manager.disconnect(websocket)