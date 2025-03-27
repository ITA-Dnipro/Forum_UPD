from typing import ClassVar
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    PROFILES_DB_HOST: str = "profiles_db"
    PROFILES_DB_PORT: int = 5432         
    PROFILES_DB_USER: str                
    PROFILES_DB_PASSWORD: str             
    PROFILES_DB_NAME: str               


    # Required fields (no defaults)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # File Storage
    IMAGE_BASE_PATH: str = "static/media/startups"
    DEFAULT_BANNER_URL: str = "static/media/startups/default_banner.jpg"


    # App
    DEBUG: bool = False

    class Config:
        env_file = ".env" 
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()