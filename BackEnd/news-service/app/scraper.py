import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from app.models import NewsModel
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://epravda.com.ua/news"

async def fetch(session, url, retries=5, backoff_factor=1):
    """
    Fetches a URL asynchronously with aiohttp and exponential backoff on failure.

    Args:
        session (aiohttp.ClientSession): The aiohttp session.
        url (str): The URL to fetch.
        retries (int): Number of retry attempts on failure.
        backoff_factor (int): Factor to increase delay between retries.

    Returns:
        str: HTML content if successful, else None.
    """
    delay = backoff_factor

    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()  # Raise HTTP errors
                return await response.text()
        
        except aiohttp.ClientError as e:
            logger.error(f"Attempt {attempt + 1}: Error fetching {url} - {e}")

        await asyncio.sleep(delay + random.uniform(0, 0.5))  # Random jitter
        delay *= 2  # Exponential backoff

    logger.error(f"Failed to fetch {url} after {retries} attempts.")


async def scrape_news():
    """Scrapes the latest business news from epravda.com.ua asynchronously"""
    try:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, URL)
            if not html:
                return []

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find("div", class_="section_articles_grid_wrapper")
            
            if not articles:
                logger.warning("No articles section found")
                return []

            latest_news = []
            article_urls = []

            for article_section in articles.find_all("div", class_="article_news", limit=5):
                title_section = article_section.find("div", class_="article_title")
                if not title_section:
                    continue
                
                link = title_section.find("a")
                if not link or "href" not in link.attrs:
                    continue
                
                article_url = link["href"]
                if not article_url.startswith("http"):
                    article_url = f"https://epravda.com.ua{article_url}"  # Ensure full URL

                article_urls.append(article_url)

            # Fetch all articles concurrently
            articles = await asyncio.gather(*(scrape_article(session, url) for url in article_urls))

            # Filter out None values (failed scrapes)
            latest_news = [news for news in articles if news]

            return latest_news

    except Exception as e:
        logger.error(f"Unexpected error in scrape_news: {e}", exc_info=True)
        return []


async def scrape_article(session, article_url):
    """Scrapes an individual article asynchronously"""
    try:
        html = await fetch(session, article_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1").text.strip() if soup.find("h1") else None
        content_section = soup.find("div", class_="post_news_text")
        content = content_section.text.strip() if content_section else None

        if not title or not content or not article_url:
                logger.warning(f"Skipping article {article_url} due to missing title or content")
                return None
        
        return NewsModel(
            title=title,
            content=content,
            link=article_url,
            published_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error scraping article {article_url}: {e}", exc_info=True)
        return None  # Ensure it returns None on failure