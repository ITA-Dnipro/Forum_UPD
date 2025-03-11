import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .es_config.es_client import elasticsearch_init
from .routes.search import search_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_routes(app: FastAPI):
    """Helper function to register routers."""
    app.include_router(search_router, prefix="/search")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager to handle startup and shutdown tasks."""
    logger.info("Startup: initializing service...")
    try:
        es_client = await elasticsearch_init()
        app.state.es_client = es_client
        yield
    except Exception as e:
        logger.exception("Startup failed. Shutting down search service...")
        raise
    finally:
        logger.info("Shutdown: cleaning up...")


app = FastAPI(
    lifespan=lifespan,
    title=settings.service_name,
    debug=settings.debug,
)

register_routes(app)
