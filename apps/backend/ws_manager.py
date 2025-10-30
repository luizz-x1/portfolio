from typing import Dict
from fastapi import WebSocket

connected_users: Dict[int, Dict[str, WebSocket]] = {}

async def connect_user(user_id: int, websocket: WebSocket, session_id: str):
    await websocket.accept()
    connected_users.setdefault(user_id, {})[session_id] = websocket
    print(f"🔵 Usuario {user_id} conectado (sesión: {session_id})")

def disconnect_user(user_id: int, session_id: str) -> bool:

    if user_id in connected_users:
        sessions = connected_users[user_id]
        if session_id in sessions:
            del sessions[session_id]
            print(f"🔴 Usuario {user_id} desconectó sesión {session_id}")

        if not sessions:
            del connected_users[user_id]
            print(f"⚫ Usuario {user_id} completamente desconectado")
            return True
    return False

# async def send_to_user(user_id: int, message: str):

#     sessions = connected_users.get(user_id, {})
#     for sid, ws in sessions.items():
#         try:
#             await ws.send_text(message)
#         except Exception:
#             print(f"No se pudo enviar mensaje a sesión {sid} del usuario {user_id}")
