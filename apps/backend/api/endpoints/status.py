from fastapi import APIRouter
from utils.redis import redis_client, ping
from services.status_service import get_user_status

router = APIRouter()

@router.get("/status/{user_id}")
async def status(user_id: str):
    status = await get_user_status(user_id)
    return {"user_id": user_id, "status": status or "offline"}

@router.get("/redis-ping")
async def test_redis():
    pong = await ping()
    return {"redis": pong}
  