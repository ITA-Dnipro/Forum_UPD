from app.celery import celery  # Import Celery app instance
from app.scraper import scrape_and_store_news  # Import your scraping function
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True)
async def scrape_news_task(self):
    """Scrapes and stores news asynchronously"""
    try:
        # Call the scrape and store news function
        result = await scrape_and_store_news()
        return result  # Return the result of the task
    except Exception as e:
        logger.error(f"Error in scrape_news_task: {e}", exc_info=True)
        raise self.retry(exc=e)  # Retry if it fails
