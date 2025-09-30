from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.admin_connections: list = []

    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        if role == "admin":
            self.admin_connections.append(websocket)
            await self.notify_admin_about_connections()

    async def handle_user_message(self, message: dict, user_id: int):

        for admin_ws in self.admin_connections:
            await admin_ws.send_json({
                "type": "new_message",
                "user_id": user_id,
                "message": message
            })

manager = ConnectionManager()