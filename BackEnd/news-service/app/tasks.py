from app.celery import celery  # Import Celery app instance
from app.scraper import scrape_and_store_news  # Import your scraping function
import logging
import asyncio
from app.database import init_db

logger = logging.getLogger(__name__)

@celery.task(bind=True)
def scrape_news_task(self):
    """Scrapes and stores news asynchronously"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Initialize Beanie before running the scraper
        loop.run_until_complete(init_db())
        loop.run_until_complete(scrape_and_store_news())
        print('success')
    except Exception as e:
        logger.error(f"Error in scrape_news_task: {e}", exc_info=True)
        raise self.retry(exc=e)  # Retry the task if it fails
    finally:
        loop.close()  # Ensure the event loop is closed properly
