from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings, logger
from .es.es_client import elasticsearch_init
from .indexes.event_service.events import EventDocument
from .indexes.forum_service.blog_posts import BlogPostDocument
from .indexes.forum_service.post_comments import PostCommentDocument
from .indexes.forum_service.question_answers import QuestionAnswerDocument
from .indexes.forum_service.questions import QuestionDocument
from .indexes.news_service.news_article import NewsArticleDocument
from .routes.search import search_router
from .utils.seed_indexes import seed_all

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
    except Exception as e:
        logger.exception("Startup failed. Shutting down search service...")
        raise

    index_classes = [
        BlogPostDocument, PostCommentDocument, QuestionDocument, QuestionAnswerDocument,
        NewsArticleDocument, EventDocument
    ]

    try:
        for cls in index_classes:
            index_name = cls.get_index_name()
            if not await es_client.indices.exists(index=index_name):
                await cls.init()
                logger.info(f"Created index: {index_name}")
            else:
                logger.info(f"Index already exists: {index_name}")
    except Exception as e:
        logger.exception(f"Error setting up Elasticsearch indices: {str(e)}")
        raise

    if settings.DEBUG:
        try:
            await seed_all()
        except Exception as e:
            logger.exception(f"Error seeding data: {str(e)}")
            raise

    try:
        yield
    finally:
        await es_client.close()
        logger.info("Shutdown: cleaning up...")


app = FastAPI(
    lifespan=lifespan,
    title=settings.SERVICE_NAME,
    debug=settings.DEBUG,
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request, exc):
    return PlainTextResponse("Rate limit exceeded", status_code=429)


app.state.limiter = limiter

register_routes(app)
