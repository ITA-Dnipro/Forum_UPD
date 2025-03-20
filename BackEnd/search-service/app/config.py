import logging
import sys

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App config settings are loaded from .env file"""

    service_name: str = Field("search-service", env="SERVICE_NAME")
    debug: bool = Field(True, env="DEBUG")

    elasticsearch_host: str = Field("http://elasticsearch:9200", env="ELASTICSEARCH_HOST")
    elasticsearch_max_retries: int = Field(5, env="ELASTICSEARCH_MAX_RETRIES")
    elasticsearch_retry_delay: int = Field(2, env="ELASTICSEARCH_RETRY_DELAY")

    events_index: str = Field("events")
    forum_blog_posts_index: str = Field("blog_posts")
    forum_blog_comments_index: str = Field("blog_comments")
    forum_questions_index: str = Field("questions")
    forum_question_answers_index: str = Field("question_answers")
    news_articles_index: str = Field("news_articles")

    @property
    def global_search_indexes(self) -> list[str]:
        """Return Elasticsearch indexes as a list for the global search."""
        return [
            self.events_index,
            self.forum_blog_posts_index,
            self.forum_questions_index,
            self.news_articles_index,
        ]

    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def setup_logging():
    """Sets up global structured logging for the search service."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    logging.getLogger("elastic_transport").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


setup_logging()
logger = logging.getLogger(settings.service_name)
