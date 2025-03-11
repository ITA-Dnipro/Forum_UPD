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
