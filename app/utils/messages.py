from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, employee_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[employee_id] = websocket

    def disconnect(self, employee_id: int):
        self.active_connections.pop(employee_id, None)

    async def send_personal_message(self, message: str, employee_id: int):
        websocket = self.active_connections.get(employee_id)
        if websocket:
            await websocket.send_text(message)