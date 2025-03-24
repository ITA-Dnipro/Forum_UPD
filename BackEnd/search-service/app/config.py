import logging
import sys

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App config settings are loaded from .env file"""

    SERVICE_NAME: str = Field("search-service", env="SERVICE_NAME")
    DEBUG: bool = Field(True, env="DEBUG")
    REDIS_URL: str = Field("redis://redis:6379", env="REDIS_URL")

    ELASTICSEARCH_HOST: str = Field("http://elasticsearch:9200", env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_MAX_RETRIES: int = Field(5, env="ELASTICSEARCH_MAX_RETRIES")
    ELASTICSEARCH_RETRY_DELAY: int = Field(2, env="ELASTICSEARCH_RETRY_DELAY")

    EVENTS_INDEX: str = Field("events")
    FORUM_BLOG_POSTS_INDEX: str = Field("blog_posts")
    FORUM_BLOG_COMMENTS_INDEX: str = Field("blog_comments")
    FORUM_QUESTIONS_INDEX: str = Field("questions")
    FORUM_QUESTION_ANSWERS_INDEX: str = Field("question_answers")
    NEWS_ARTICLES_INDEX: str = Field("news_articles")

    @property
    def global_search_indexes(self) -> list[str]:
        """Return Elasticsearch indexes as a list for the global search."""
        return [
            self.EVENTS_INDEX,
            self.FORUM_BLOG_POSTS_INDEX,
            self.FORUM_QUESTIONS_INDEX,
            self.NEWS_ARTICLES_INDEX,
        ]

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def setup_logging():
    """Sets up global structured logging for the search service."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    logging.getLogger("elastic_transport").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


setup_logging()
logger = logging.getLogger(settings.SERVICE_NAME)
