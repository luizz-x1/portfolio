from typing import Dict
from fastapi import WebSocket, status
from utils.redis import publish
from utils.security import verify_token
from crud import crud_meetings
import asyncio, json

# Usuarios conectados con sus sesiones activas
connected_users: Dict[int, Dict[str, WebSocket]] = {}


async def handle_meeting_event(user_id: int, data: str, db):

    try:
        parts = data.split(":")
        if len(parts) != 4:
            print(f"⚠️ Formato inválido para meeting: {data}")
            return

        _, target_user_id, chat_id, status = parts
        target_user_id = int(target_user_id)
        chat_id = int(chat_id)

        if status not in ("pending", "accepted", "canceled"):
            print(f"⚠️ Estado inválido de reunión: {status}")
            return

        # Guardar en DB si la reunión fue aceptada
        if status == "accepted":
            crud_meetings.create_meeting(
                db=db,
                chat_id=chat_id,
                organizer_id=user_id,
                title=f"Reunión del chat {chat_id}",
                description="Reunión confirmada entre participantes.",
                meeting_link=None,
                scheduled_at=datetime.now(),
                status="accepted"
            )

        await publish(f"user:{target_user_id}", json.dumps({
            "type": "meeting",
            "from": user_id,
            "chat_id": chat_id,
            "status": status
        }))

        print(f"📅 Reunión '{status}' entre {user_id} y {target_user_id} (chat {chat_id})")

    except Exception as e:
        print(f"❌ Error al manejar evento de reunión: {e}")

        

async def connect_user(user_id: int, websocket: WebSocket, session_id: str):
    """Acepta el WebSocket y registra la sesión activa del usuario."""
    await websocket.accept()
    connected_users.setdefault(user_id, {})[session_id] = websocket
    print(f"🔵 Usuario {user_id} conectado (sesión: {session_id})")


def disconnect_user(user_id: int, session_id: str) -> bool:
    """Elimina una sesión y retorna True si el usuario quedó sin conexiones activas."""
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


async def send_message_to_user(user_id: int, message_data: dict):
    """Envía un mensaje por Redis al usuario si está conectado."""
    if user_id in connected_users and connected_users[user_id]:
        await publish(f"user:{user_id}", json.dumps(message_data))
        return True
    return False  


async def authenticate_websocket(websocket: WebSocket, user_id: int) -> dict:
    """Valida el token y asegura que coincida con el user_id de la conexión."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        token_user_id = int(payload.get("user_id"))
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    if token_user_id != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    return payload


async def notify_contacts_status(user_id: int, contacts: list[int], status_value: str):
    """Publica el cambio de estado (online/offline) del usuario a sus contactos."""
    for cid in contacts:
        await publish(f"user:{cid}", json.dumps({
            "type": "status",
            "user_id": user_id,
            "status": status_value
        }))


async def send_online_contacts(websocket: WebSocket, contacts: list[int]):
    """Envía al usuario la lista de contactos que están en línea."""
    for cid in contacts:
        if cid in connected_users:
            await websocket.send_text(json.dumps({
                "type": "status",
                "user_id": cid,
                "status": "online"
            }))


async def start_redis_listener(pubsub_user, websocket: WebSocket):
    """Escucha mensajes del canal Redis y los reenvía al cliente WebSocket."""
    while True:
        message_user = await pubsub_user.get_message(ignore_subscribe_messages=True, timeout=0.1)
        if message_user:
            data = message_user["data"]
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            try:
                parsed = json.loads(data)
                await websocket.send_text(json.dumps(parsed))
            except json.JSONDecodeError:
                await websocket.send_text(data)
        await asyncio.sleep(0.01)
