from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Model
from os import environ
from dotenv import load_dotenv


load_dotenv()

connect_str = f"postgresql+psycopg://{environ['DB_USER']}:{environ['DB_PASSWORD']}@{environ['DB_HOST']}:{environ['DB_PORT']}/{environ['DB_NAME']}"
engine = create_async_engine(
    connect_str
)

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

