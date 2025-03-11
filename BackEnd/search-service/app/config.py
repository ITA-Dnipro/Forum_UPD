from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App config settings are loaded from .env file"""

    service_name: str = Field("search-service", env="SERVICE_NAME")
    debug: bool = Field(True, env="DEBUG")

    elasticsearch_host: str = Field("http://elasticsearch:9200", env="ELASTICSEARCH_HOST")
    elasticsearch_max_retries: int = Field(5, env="ELASTICSEARCH_MAX_RETRIES")
    elasticsearch_retry_delay: int = Field(2, env="ELASTICSEARCH_RETRY_DELAY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
