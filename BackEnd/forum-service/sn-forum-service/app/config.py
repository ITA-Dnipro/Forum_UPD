from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    
    app_name: str = Field("Forum MicroService", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    
    cassandra_contact_points: list = Field(["cassandra"], env="CASSANDRA_CONTACT_POINTS")
    cassandra_host: str = Field("cassandra", env="CASSANDRA_HOST")
    cassandra_port: int = Field(9052, env="CASSANDRA_PORT")
    cassandra_keyspace: str = Field("forum_keyspace", env="CASSANDRA_KEYSPACE")
    cassandra_username: str = Field("cassandra", env="CASSANDRA_USERNAME")
    cassandra_password: str = Field("cassandra", env="CASSANDRA_PASSWORD")
    
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()