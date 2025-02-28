from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    
    app_name: str = Field("Forum MicroService", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    
    cassandra_contact_points: List[str] = Field(["cassandra"], env="CASSANDRA_CONTACT_POINTS") 
    cassandra_port: int = Field(9042, env="CASSANDRA_PORT")
    cassandra_keyspace: str = Field("forum_keyspace", env="CASSANDRA_KEYSPACE")
    cassandra_username: str = Field("cassandra", env="CASSANDRA_USERNAME")
    cassandra_password: str = Field("cassandra", env="CASSANDRA_PASSWORD")
    
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")
    
    cors_origins: str = Field("http://localhost", env="CORS_ORIGINS")

    cassandra_max_retries: int = Field(5, env="CASSANDRA_MAX_RETRIES")
    cassandra_retry_delay: int = Field(5, env="CASSANDRA_RETRY_DELAY")

    class Config:
        env_file = ".env"
        
settings = Settings()