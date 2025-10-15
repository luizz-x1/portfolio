import redis.asyncio as redis

redis_client: redis.Redis | None = None

async def init_redis():
    global redis_client
    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
    pong = await redis_client.ping()
    print("✅ Conectado a Redis:", pong)


async def get_redis():
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis no inicializado.")
    return redis_client


async def ping():
    client = await get_redis()
    return await client.ping()

async def publish(channel: str, message: str):
    await redis_client.publish(channel, message)

async def subscribe(channel: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    return pubsub