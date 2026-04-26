from fastapi import WebSocket
from typing import Dict, List, Any
import json

class ConnectionManager:
    def __init__(self):
        # Almacena conexiones por ID de usuario o rol
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal_message(self, message: Any, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_text(json.dumps(message))

    async def broadcast(self, message: Any):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()
