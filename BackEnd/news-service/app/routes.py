# routes.py
from fastapi import APIRouter, Query, HTTPException
from app.models import NewsModel
from app.celery import celery
from beanie import PydanticObjectId

router = APIRouter()


@router.get("/news")
async def get_news(skip: int = 0, limit: int = 3):
    news = await NewsModel.find_all().skip(skip).limit(limit).to_list()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news


@router.get("/news/{news_id}")
async def get_article(news_id: PydanticObjectId):
    news = await NewsModel.get(news_id)
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news

@router.post("/scrape/")
async def trigger_scraping():
    """Trigger the Celery task to scrape news"""
    task = celery.send_task("app.tasks.scrape_news_task")  # Reference the task in tasks.py
    return {"message": "Scraping task started", "task_id": task.id}

@router.delete("/news/{news_id}")
async def delete_news(news_id: PydanticObjectId):
    news = await NewsModel.get(news_id)

    if news:
        await news.delete()
        return {"message": "News deleted"}
    
    raise HTTPException(status_code=204, detail="News not found")



