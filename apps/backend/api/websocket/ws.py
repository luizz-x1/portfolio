from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ws_manager import connect_user, disconnect_user, connected_users
from utils.redis import publish, subscribe
import asyncio
from services.status_service import set_user_status
from services.chat_service import get_contacts_for_notifications

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await connect_user(user_id, websocket)

    contacts = await get_contacts_for_notifications(user_id)
    await set_user_status(user_id, "online")

    for cid in contacts:
        if cid in connected_users:
            await websocket.send_text(f"user:{cid}:online")

    for cid in contacts:
        await publish(f"user:{cid}", f"user:{user_id}:online")

    user_channel = f"user:{user_id}"
    pubsub_user = await subscribe(user_channel)

    async def listen_pubsub():
        """Escucha mensajes personales (typing, mensajes, etc.)."""
        while True:
            message_user = await pubsub_user.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message_user:
                await websocket.send_text(f"📩 Evento personal: {message_user['data']}")
            await asyncio.sleep(0.01)

    listener_task = asyncio.create_task(listen_pubsub())

    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("typing:"):
                target_user_id = int(data.split(":")[1])
                await publish(f"user:{target_user_id}", f"typing:{user_id}")

            elif data.startswith("message:"):
                target_user_id, msg = data.split(":")[1], ":".join(data.split(":")[2:])
                await publish(f"user:{target_user_id}", f"message:{user_id}:{msg}")

    except WebSocketDisconnect:
        disconnect_user(user_id)
        await set_user_status(user_id, "offline")

        for cid in contacts:
            await publish(f"user:{cid}", f"user:{user_id}:offline")

    finally:
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass

        if not websocket.client_state.name in ("DISCONNECTED", "CLOSED"):
            try:
                await websocket.close()
            except Exception:
                pass
