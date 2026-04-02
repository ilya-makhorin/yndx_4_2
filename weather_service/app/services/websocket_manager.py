from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict[str, Any]) -> None:
        disconnected_connections: list[WebSocket] = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected_connections.append(websocket)

        for websocket in disconnected_connections:
            self.disconnect(websocket)


weather_ws_manager = ConnectionManager()