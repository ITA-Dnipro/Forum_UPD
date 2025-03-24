import json
from collections import defaultdict

from dotenv import load_dotenv
from elasticsearch_dsl import AsyncSearch
from fastapi import APIRouter, Depends, Request, HTTPException, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing_extensions import Annotated

from ..config import logger, settings
from ..search_processing.local_search_params import (
    EventSearchParams,
    BlogPostSearchParams,
    BlogCommentSearchParams,
    QuestionSearchParams,
    QuestionAnswerSearchParams,
    NewsSearchParams
)
from ..search_processing.search_processor import (
    EventSearchProcessor,
    BlogPostSearchProcessor,
    BlogCommentSearchProcessor,
    QuestionSearchProcessor,
    QuestionAnswerSearchProcessor,
    NewsSearchProcessor
)

search_router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

load_dotenv()

event_search_processor = EventSearchProcessor()
blog_post_search_processor = BlogPostSearchProcessor()
blog_comment_search_processor = BlogCommentSearchProcessor()
question_search_processor = QuestionSearchProcessor()
question_answer_search_processor = QuestionAnswerSearchProcessor()
news_search_processor = NewsSearchProcessor()


async def get_es_client(request: Request):
    """Retrieves the Elasticsearch client from the FastAPI app state."""
    es_client = getattr(request.app.state, "es_client")

    if not await es_client.ping():
        logger.error("Failed to reach Elasticsearch")
        raise HTTPException(status_code=503, detail="Service is unreachable")

    return es_client


async def get_redis_client(request: Request):
    """Retrieves the Redis client from the FastAPI app state."""
    redis_client = getattr(request.app.state, "redis")

    if not await redis_client.ping():
        logger.error("Failed to reach Redis")
        raise HTTPException(status_code=503, detail="Service is unreachable")

    return redis_client


@search_router.get(
    "/",
    summary="Global search"
)
@limiter.limit("20/minute")
async def global_search(
        request: Request,
        q: str = Query(..., description="Query string for the search"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Number of results per page"),
        es_client=Depends(get_es_client)
):
    """
    Global search endpoint that performs a multi-index search using a multi_match query,
    with pagination. Matches in the title have a higher score. Fuzzy matching is enabled
    to return similar results as well. The results are grouped by index.

    Args:
    - q: The search query string.
    - page: The page number for pagination.
    - page_size: Number of results per page.

    Response:
    - A JSON object with grouped search results; each key represents the source index.
    """
    cache_key = f"global_search:{q}:{page}:{page_size}"
    redis_client = request.app.state.redis

    cached = await redis_client.get(cache_key)
    if cached:
        logger.info("Returning cached search results")
        return json.loads(cached)

    offset = (page - 1) * page_size

    s = AsyncSearch(using=es_client, index=settings.global_search_indexes).query(
        "multi_match",
        query=q,
        fields=["title^2", "content"],
        fuzziness="AUTO"
    ).extra(from_=offset, size=page_size)

    try:
        response = await s.execute()
        result = defaultdict(list)
        for hit in response:
            result_item = {
                "id": hit.meta.id,
                "title": hit.title,
                "content": hit.content
            }
            result[hit.meta.index].append(result_item)

    except Exception as e:
        logger.error(f"Error executing Elasticsearch search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search service is currently unavailable. Please try again later."
        )

    logger.info(f"Global search succeeded, returning results from {len(result)} index(es)")
    cache_data = json.dumps({"results": dict(result)})
    await redis_client.set(cache_key, cache_data, ex=120)
    return {"results": result}


@search_router.get("/service/events/")
async def search_events(
        request: Request,
        params: Annotated[EventSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    Event search endpoint, that uses multi_match query.
    Matches in the title have a higher score.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts events based on various parameters.

    Args:
    - query: text to search within titles and content.
    - category: filter by the category name.
    - event_type: filter by the type of event.
    - event_status: filter by the status of the event.
    - location: filter by the location of the event.
    - date_from: filter events from this date onward.
    - sort_by: field name to sort results (default: "date").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - A JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for events requested")
    response = await event_search_processor.search(es_client, redis_client, params)
    logger.info("Search for events was successful")
    return response


@search_router.get("/service/blog-posts/")
async def search_blog_posts(
        request: Request,
        params: Annotated[BlogPostSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    Blog posts search endpoint, that uses multi_match query.
    Matches in the title have a higher score.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts blog posts based on various parameters.

    Args:
    - query: text to search within titles and content.
    - author_id: filter by the author's ID.
    - category: filter by the category name.
    - tag: filter by the tag name.
    - created_from: filter posts created from this date onward.
    - sort_by: field name to sort results (default: "likes_count").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for blog posts requested")
    response = await blog_post_search_processor.search(es_client, redis_client, params)
    logger.info("Search for blog posts was successful")
    return response


@search_router.get("/service/blog-comments/")
async def search_blog_comments(
        request: Request,
        params: Annotated[BlogCommentSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    Blog comments search endpoint, that uses match query.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts blog comments based on various parameters.

    Args:
    - query: text to search within content.
    - author_id: filter by the author's ID.
    - created_from: filter comments created from this date onward.
    - sort_by: field name to sort results (default: "likes_count").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for blog comments requested")
    response = await blog_comment_search_processor.search(es_client, redis_client, params)
    logger.info("Search for blog comments was successful")
    return response


@search_router.get("/service/questions/")
async def search_questions(
        request: Request,
        params: Annotated[QuestionSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    Questions search endpoint, that uses multi_match query.
    Matches in the title have a higher score.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts questions based on various parameters.

    Args:
    - query: text to search within titles and content.
    - author_id: filter by the author's ID.
    - question_status: filter by the question status.
    - created_from: filter questions created from this date onward.
    - sort_by: field name to sort results (default: "views_count").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for questions requested")
    response = await question_search_processor.search(es_client, redis_client, params)
    logger.info("Search for questions was successful")
    return response


@search_router.get("/service/question-answers/")
async def search_question_answers(
        request: Request,
        params: Annotated[QuestionAnswerSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    Question answers search endpoint, that uses match query.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts question answers based on various parameters.

    Args:
    - query: text to search within the content.
    - author_id: filter by the author's ID.
    - created_from: filter answers created from this date onward.
    - sort_by: field name to sort results (default: "likes_count").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for question answers requested")
    response = await question_answer_search_processor.search(es_client, redis_client, params)
    logger.info("Search for question answers was successful")
    return response


@search_router.get("/service/news/")
async def search_news(
        request: Request,
        params: Annotated[NewsSearchParams, Query()],
        es_client=Depends(get_es_client),
        redis_client=Depends(get_redis_client)
):
    """
    News search endpoint, that uses multi_match query.
    Matches in the title have a higher score.\n
    Fuzzy matching is enabled to return similar results as well.
    Filters and sorts questions based on various parameters.

    Args:
    - query: text to search within titles and content.
    - published_from: filter articles published from this date onward.
    - sort_by: field name to sort results (default: "published_at").
    - sort_order: sort order, either "asc" or "desc".
    - page: Page number for pagination.
    - page_size: Number of results per page.

    Response:
    - JSON object with 'total_records' and 'records_list'.
    """
    logger.info("Search for news requested")
    response = await news_search_processor.search(es_client, redis_client, params)
    logger.info("Search for news was successful")
    return response


@search_router.get("/suggestions/")
@limiter.limit("20/minute")
async def get_suggestions(request: Request, es_client=Depends(get_es_client)):
    """Endpoint for search suggestions."""
    logger.info("Suggestions requested")
    return {"message": "Suggestions are working"}
