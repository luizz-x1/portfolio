from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import asyncio, json
from ws_manager import connect_user, disconnect_user, connected_users
from utils.redis import publish, subscribe
from services.status_service import set_user_status
from services.chat_service import get_contacts_for_notifications
from utils.security import verify_token

router = APIRouter()

# --- Seguridad ---
async def authenticate_websocket(websocket: WebSocket, user_id: int) -> dict:
    """Valida el token JWT y que coincida con el user_id."""
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


# --- Notificaciones ---
async def notify_contacts_status(user_id: int, contacts: list[int], status_value: str):
    """Notifica a los contactos el estado del usuario."""
    for cid in contacts:
        await publish(f"user:{cid}", json.dumps({
            "type": "status",
            "user_id": user_id,
            "status": status_value
        }))


async def send_online_contacts(websocket: WebSocket, contacts: list[int]):
    """Envía al cliente los contactos que están online."""
    for cid in contacts:
        if cid in connected_users:
            await websocket.send_text(json.dumps({
                "type": "status",
                "user_id": cid,
                "status": "online"
            }))


# --- Escucha de Redis ---
async def start_redis_listener(pubsub_user, websocket: WebSocket):
    """Escucha eventos personales desde Redis."""
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


# --- WebSocket ---
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Canal WebSocket seguro y en tiempo real."""
    # Seguridad
    payload = await authenticate_websocket(websocket, user_id)
    if not payload:
        return

    # Conexión
    await connect_user(user_id, websocket)
    await set_user_status(user_id, "online")

    # Notificación de estado
    contacts = await get_contacts_for_notifications(user_id)
    await send_online_contacts(websocket, contacts)
    await notify_contacts_status(user_id, contacts, "online")

    # Escucha de mensajes en Redis
    user_channel = f"user:{user_id}"
    pubsub_user = await subscribe(user_channel)
    listener_task = asyncio.create_task(start_redis_listener(pubsub_user, websocket))

    try:
        # Escucha del cliente
        while True:
            data = await websocket.receive_text()

            # Evento de escritura
            if data.startswith("typing:"):
                try:
                    target_user_id = int(data.split(":", 1)[1])
                    await publish(f"user:{target_user_id}", f"typing:{user_id}")
                except Exception:
                    continue

            # Envío de mensaje
            elif data.startswith("message:"):
                parts = data.split(":", 2)
                if len(parts) < 3:
                    continue
                try:
                    target_user_id = int(parts[1])
                    msg = parts[2]
                    await publish(f"user:{target_user_id}", json.dumps({
                        "type": "message",
                        "from": user_id,
                        "content": msg
                    }))
                except Exception:
                    continue

    except WebSocketDisconnect:
        # Desconexión
        disconnect_user(user_id)
        await set_user_status(user_id, "offline")
        await notify_contacts_status(user_id, contacts, "offline")

    finally:
        # Limpieza
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass

        if websocket.client_state.name not in ("DISCONNECTED", "CLOSED"):
            try:
                await websocket.close()
            except Exception:
                pass
