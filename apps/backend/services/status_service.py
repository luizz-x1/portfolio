import json
import redis.asyncio as redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

async def set_user_status(user_id: str, status: str):
    """Guarda el estado del usuario y lo publica a Redis"""
    key = f"status:{user_id}"
    await r.set(key, status)
    message = json.dumps({"user_id": user_id, "status": status})
    await r.publish("status_updates", message)

async def get_user_status(user_id: str):
    """Obtiene el estado actual del usuario"""
    key = f"status:{user_id}"
    return await r.get(key)
