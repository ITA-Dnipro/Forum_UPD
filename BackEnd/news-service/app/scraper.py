# scraper.py
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from app.models import NewsModel
import requests

URL = "https://epravda.com.ua/news"

def scrape_news():
    """ Scrapes the latest business news from epravda.com.ua """

    response = requests.get(URL)
    if response.status_code != 200:
        print("Failed to fetch main news page")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find("div", class_="section_articles_grid_wrapper")
    
    if not articles:
        print("No articles section found")
        return []

    latest_news = []
    
    
    for article_section in articles.find_all("div", class_="article_news", limit=5):
        title_section = article_section.find("div", class_="article_title")
        if not title_section:
            continue
        
        link = title_section.find("a")
        if not link or "href" not in link.attrs:
            continue
        
        article_url = link["href"]
        article_news = scrape_article(article_url)

        if article_news:
            latest_news.append(article_news)

    return latest_news



def scrape_article(article_url):
    '''Scraping article from the page'''
    article_resp = requests.get(article_url)

    article_soup = BeautifulSoup(article_resp.text, "html.parser")
    title = article_soup.find("h1").text.strip() if article_soup.find("h1") else "No Title"
    content = article_soup.find("div", class_="post_news_text").text.strip() if article_soup.find("div", class_="post_news_text") else "No Content"

    news = NewsModel(title=title, content=content, link=article_url, published_at=datetime.now())
    return news