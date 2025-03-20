from app.celery import celery
from app.scraper import scrape_and_store_news
import logging
import asyncio
from app.database import init_db

logger = logging.getLogger(__name__)

@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,          
    retry_kwargs={"max_retries": 5},
)
def scrape_news_task(self):
    """Scrapes and stores news asynchronously"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(init_db())

        loop.run_until_complete(scrape_and_store_news())
    except Exception as e:
        logger.error(f"Error in scrape_news_task: {e}", exc_info=True)
        raise e
    finally:
        loop.close()  
