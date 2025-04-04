# routes.py
from fastapi import APIRouter, Query, HTTPException
from app.models import NewsModel
from app.celery import celery
from beanie import PydanticObjectId
from app.redis import redis
from app.utils import delete_news_from_cache
from app.tasks import scrape_news_task
import json

router = APIRouter()


@router.get("/news")
async def get_news(skip: int = 0, limit: int = 3):
    news = await NewsModel.find(NewsModel.deleted == False).sort(-NewsModel.published_at).skip(skip).limit(limit).to_list()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news


@router.get("/news/{news_id}")
async def get_article(news_id: PydanticObjectId):
    news = await NewsModel.get(news_id)
    
    if not news or news.deleted:
        raise HTTPException(status_code=404, detail="News not found")

    return news


@router.get("/news/recent/")
async def get_recent_news():
    try:
        cached_news = await redis.lrange("recent_news", 0, -1)  # Fetch all items from list
        print(cached_news)
        if cached_news:
            return [json.loads(news) for news in cached_news]  # Decode each item from JSON
        return {"message": "No recent news found in cache."}
    except:
        raise HTTPException(status_code=500, detail="We got problem on the server. It is not your fault." )


@router.post("/scrape/")
async def trigger_scraping():
    """Trigger the Celery task to scrape news"""
    task = scrape_news_task.apply_async()
    return {"message": "Scraping task started", "task_id": task.id}


@router.delete("/news/{news_id}")
async def delete_news(news_id: PydanticObjectId):
    news = await NewsModel.get(news_id)

    if news:
        news.deleted = True
        await news.save()

        await delete_news_from_cache(news_id)

        return {"message": "News deleted"}
    
    raise HTTPException(status_code=204, detail="News not found")



