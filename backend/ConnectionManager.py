from fastapi import WebSocket
from typing import List
from starlette.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_connections_dict: dict[str,WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        # self.active_connections.append(websocket)
        self.active_connections_dict[client_id] = websocket

    def disconnect(self, websocket: WebSocket, clientID:str):
        # self.active_connections.remove(websocket)
        del self.active_connections_dict[clientID]
    

    async def broadcast(self, message: dict, client_id: str):
        if client_id not in self.active_connections_dict:
            print(f"Client {client_id} already disconnected, skipping broadcast")
            return
        
        try:
            ws = self.active_connections_dict[client_id]
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_json(message)
            else:
                del self.active_connections_dict[client_id]
        except RuntimeError:
            del self.active_connections_dict[client_id]         


manager = ConnectionManager()
