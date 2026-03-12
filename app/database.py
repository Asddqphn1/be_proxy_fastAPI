import redis.asyncio as redis
from app.config import security_settings

pool = redis.ConnectionPool.from_url(
    f"redis://{security_settings.REDIS_HOST}:{security_settings.REDIS_PORT}", 
    decode_responses=True
)

async def get_redis():
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()