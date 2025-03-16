import redis.asyncio as red

REDIS_URL = "redis://redis_cache"

redis = red.Redis.from_url(REDIS_URL, decode_responses=True)
