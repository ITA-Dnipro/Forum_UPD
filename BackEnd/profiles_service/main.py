import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from utils.producer import init_producer, shutdown_producer
from routers import investors, categories, regions, images, startups
from utils.consumers import ConsumerManager
from consumers.new_profile import consume_new_user_profiles
from contextlib import asynccontextmanager
from core.settings import settings



@asynccontextmanager
async def lifespan(app):
    await init_producer(settings.KAFKA_BROKER)
    consumer = await ConsumerManager.create_consumer(topic="new_user_profile")
    asyncio.create_task(consume_new_user_profiles(consumer=consumer))
    yield
    await shutdown_producer()
    await ConsumerManager.shutdown_all()



app = FastAPI(root_path="/api", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(startups.router, prefix="/startup_profiles")
app.include_router(investors.router, prefix="/investor_profiles")
app.include_router(categories.router, prefix="/startup_categories")
app.include_router(regions.router, prefix="/regions")
app.include_router(images.router, prefix="/images")
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
