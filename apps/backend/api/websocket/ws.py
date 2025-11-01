from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio, json

# --- Utils ---
from utils.redis import publish, subscribe
from utils.security import verify_token
from crud.crud_messages import get_pending_messages, update_status
from config.database import get_db

# --- Services ---
from services.ws_service import (
    connect_user, disconnect_user, connected_users,
    send_message_to_user, authenticate_websocket,
    notify_contacts_status, send_online_contacts,
    start_redis_listener
)
from services.status_service import set_user_status
from services.chat_service import get_contacts_for_notifications

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Maneja conexión WebSocket, autenticación, mensajes y estados de usuario."""
    session_id = websocket.query_params.get("session_id", "default")
    db = next(get_db())

    # Autenticar conexión
    payload = await authenticate_websocket(websocket, user_id)
    if not payload:
        return

    # Registrar conexión y estado
    await connect_user(user_id, websocket, session_id)
    await set_user_status(user_id, "online")

    # Notificar contactos y enviar lista de conectados
    contacts = await get_contacts_for_notifications(db, user_id)
    await send_online_contacts(websocket, contacts)
    await notify_contacts_status(user_id, contacts, "online")

    # Enviar mensajes pendientes (sin entregar)
    offline_messages = get_pending_messages(db, user_id)
    for msg in offline_messages:
        await websocket.send_text(json.dumps({
            "type": "message",
            "message_id": msg.id,
            "from": msg.sender_id,
            "chat_id": msg.chat_id,
            "content": msg.content
        }))
        update_status(db, msg.id, "delivered")
        await publish(f"user:{msg.sender_id}", json.dumps({
            "type": "status_update",
            "message_id": msg.id,
            "status": "delivered"
        }))

    # Escuchar canal Redis del usuario
    user_channel = f"user:{user_id}"
    pubsub_user = await subscribe(user_channel)
    listener_task = asyncio.create_task(start_redis_listener(pubsub_user, websocket))

    try:
        # Escuchar mensajes entrantes desde el cliente
        while True:
            data = await websocket.receive_text()

            # Usuario escribiendo
            if data.startswith("typing:"):
                try:
                    target_user_id = int(data.split(":", 1)[1])
                    await publish(f"user:{target_user_id}", f"typing:{user_id}")
                except Exception:
                    continue

            # Mensaje leído
            elif data.startswith("read:"):
                message_id = int(data.split(":")[1])
                await update_status(db, message_id, "read")

                # Notificar al emisor
                msg = await crud_messages.get_message(db, message_id)
                await publish(f"user:{msg.sender_id}", json.dumps({
                    "type": "status_update",
                    "message_id": message_id,
                    "status": "read"
                }))

    except WebSocketDisconnect:
        # Desconexión del usuario
        no_more_sessions = disconnect_user(user_id, session_id)
        if no_more_sessions:
            await set_user_status(user_id, "offline")
            await notify_contacts_status(user_id, contacts, "offline")

    finally:
        # Cerrar listener y conexión
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
