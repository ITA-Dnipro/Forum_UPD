import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import mapped_column, DeclarativeBase
from sqlalchemy import String
from typing import Annotated

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

str_100 = Annotated[str, 100]
str_30 = Annotated[str, 30]
intpk = Annotated[int, mapped_column(primary_key=True)]

class Base(DeclarativeBase):
    type_annotation_map = {
        str_100: String(100),
        str_30: String(30)
    }
    pass

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session