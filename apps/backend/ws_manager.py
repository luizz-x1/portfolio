from typing import Dict
from fastapi import WebSocket

connected_users: Dict[int, WebSocket] = {}

async def connect_user(user_id: int, websocket: WebSocket):
    """Registra un nuevo usuario y acepta la conexión WebSocket."""
    await websocket.accept()
    connected_users[user_id] = websocket
    print(f"🔵 Usuario {user_id} conectado")

def disconnect_user(user_id: int):
    """Elimina al usuario del registro cuando se desconecta."""
    if user_id in connected_users:
        del connected_users[user_id]
        print(f"🔴 Usuario {user_id} desconectado")

# async def send_to_user(user_id: int, message: str):
#     """Envía un mensaje directo a un usuario específico """
#     ws = connected_users.get(user_id)
#     if ws:
#         await ws.send_text(message)
