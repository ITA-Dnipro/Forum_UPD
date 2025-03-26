import json
from bson import ObjectId
from datetime import datetime
from pathlib import Path
from app.redis import redis
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
      

def load_lua_script(path):
    """Loads the Lua script for Redis caching."""
    try:
        logger.info("Entering Lua script loader...")
        with open(path, "r") as file:
            logger.info("Reading Lua script file...")
            return file.read()
    
    except FileNotFoundError:
        logger.error(f"Error: Lua script file '{path}' not found.")
        return None
    
    except PermissionError:
        logger.error(f"Error: No permission to read the Lua script file '{path}'.")
        return None
    
    except Exception as e:
        logger.exception(f"Unexpected error while loading Lua script: {e}")
        return None
    

async def update_news_cache(news_articles, max_cache_size=8):
    """Updates Redis cache with new news articles using Lua script."""
    cache_key = "recent_news"

    # Convert articles to JSON strings (each article separately)
    articles_json = [json.dumps(n.dict(), cls=MongoJSONEncoder) for n in news_articles]

    logger.info("Updating Redis cache with new articles...")

    try:
        # Pass articles as separate arguments
        result = await redis.eval(LUA_SCRIPT_UPDATE, 1, cache_key, *articles_json, max_cache_size)
        logger.info(f"Cache update result: {result}")

    except Exception as e:
        logger.exception(f"Error updating news cache: {e}")



async def delete_news_from_cache(news_id):
    """Deletes a specific news article from Redis cache using Lua script."""
    cache_key = "recent_news"

    logger.info("Deleting article from Redis cache")

    try:
        result = await redis.eval(LUA_SCRIPT_DELETE, 1, cache_key, str(news_id))
        logger.info(f"News Deleted: {result}")

    except Exception as e:
        logger.exception(f"Error deleting news from cache: {e}")


LUA_SCRIPT_UPDATE = load_lua_script(Path(__file__).parent / "scripts" / "update_news.lua")
LUA_SCRIPT_DELETE = load_lua_script(Path(__file__).parent / "scripts" / "delete_news.lua")
