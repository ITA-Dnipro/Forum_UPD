import redis.asyncio as red

# Redis URL (Update if running locally or in Docker)
REDIS_URL = "redis://redis_cache"

# Create Redis connection
redis = red.Redis.from_url(REDIS_URL, decode_responses=True)
