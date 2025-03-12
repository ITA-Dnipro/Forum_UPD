from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings, logger
from .es_config.es_client import elasticsearch_init
from .routes.search import search_router

limiter = Limiter(key_func=get_remote_address)


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


@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request, exc):
    return PlainTextResponse("Rate limit exceeded", status_code=429)

app.state.limiter = limiter

register_routes(app)
