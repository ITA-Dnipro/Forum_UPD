import redis.asyncio as redis
from ..config import logger, settings


async def get_redis_client():
    """
    Initialize and return an asynchronous Redis client.
    """
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        if await redis_client.ping():
            logger.info("Connected to Redis")
        return redis_client
    except Exception as e:
        logger.exception(f"Failed to connect to Redis: {e}")
        raise
