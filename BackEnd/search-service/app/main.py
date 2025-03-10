import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .routes.search import search_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_routes(app: FastAPI):
    """Helper function to register routers."""
    app.include_router(search_router, prefix="/search")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: initializing service...")
    yield
    logger.info("Shutdown: cleaning up...")


app = FastAPI(
    lifespan=lifespan,
    title=settings.service_name,
    debug=settings.debug,
)

register_routes(app)
