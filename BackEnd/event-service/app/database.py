import os
from dotenv import load_dotenv
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")
print(f"Connecting to database: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session