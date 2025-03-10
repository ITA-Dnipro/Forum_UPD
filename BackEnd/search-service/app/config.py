from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """App config settings are loaded from .env file"""

    service_name: str = Field("search-service", env="SERVICE_NAME")
    debug: bool = Field(True, env="DEBUG")

    elasticsearch_host: str = Field("http://elasticsearch:9200", env="ELASTICSEARCH_HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
