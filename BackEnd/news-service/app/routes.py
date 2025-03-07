# routes.py
from fastapi import APIRouter, Query, HTTPException
from app.models import NewsModel
from app.scraper import scrape_news
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

@router.post("/scrape")
async def scrape_and_store_news():
    """Scrapes the latest 5 news articles and stores them in MongoDB if not duplicates."""
    
    latest_news = await scrape_news()
    
    if not latest_news:
        raise HTTPException(status_code=404, detail="No news found")

    saved_news = []
    skipped_news = []

    for news in latest_news:
        # Check if the article already exists in MongoDB
        existing = await NewsModel.find_one({"link": news.link})
        if existing:
            skipped_news.append(news)
            continue  

        # Insert new news into MongoDB
        inserted = await NewsModel.insert_one(news)
        if inserted.id:
            saved_news.append(news)

    return {
        "message": "Scraping completed",
        "saved_news_count": len(saved_news),
        "skipped_news_count": len(skipped_news),
        "saved_news": saved_news,
        "skipped_news": skipped_news
    }


@router.delete("/news/{news_id}")
async def delete_news(news_id: PydanticObjectId):
    news = await NewsModel.get(news_id)

    if news:
        await news.delete()
        return {"message": "News deleted"}
    
    raise HTTPException(status_code=204, detail="News not found")



