import json
from bson import ObjectId
from datetime import datetime
from pathlib import Path
from app.redis import redis


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
    

def load_lua_script(path):
    """Loads the Lua script for Redis caching."""
    print("enter lua")
    with open(path, "r") as file:
        print("We are reading file")
        return file.read()
    

async def update_news_cache(news_articles, max_cache_size=8):
    """Updates Redis cache with new news articles using Lua script."""
    cache_key = "recent_news"
    news_json = json.dumps([n.dict() for n in news_articles], cls=MongoJSONEncoder)
    print("entered")
    result = await redis.eval(LUA_SCRIPT_UPDATE, 1, cache_key, news_json, max_cache_size)
    print(result)


async def delete_news_from_cache(news_id):
    """Deletes a specific news article from Redis cache using Lua script."""
    cache_key = "recent_news"
    result = await redis.eval(LUA_SCRIPT_DELETE, 1, cache_key, str(news_id))
    print(await redis.get("recent_news"))
    print("News Deleted:", result)

LUA_SCRIPT_UPDATE = load_lua_script(Path(__file__).parent / "scripts" / "update_news.lua")
LUA_SCRIPT_DELETE = load_lua_script(Path(__file__).parent / "scripts" / "delete_news.lua")
