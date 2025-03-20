import os
from collections import defaultdict

from dotenv import load_dotenv
from elasticsearch_dsl import AsyncSearch
from fastapi import APIRouter, Depends, Request, HTTPException, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import logger, settings
from ..schema.global_search import GlobalSearchResponse

search_router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

load_dotenv()

VALID_SERVICES = os.getenv("VALID_SERVICES", "").split(",") if os.getenv("VALID_SERVICES") else []


async def get_es_client(request: Request):
    """Retrieves the Elasticsearch client from the FastAPI app state."""
    es_client = getattr(request.app.state, "es_client")

    if not await es_client.ping():
        logger.error("Failed to reach Elasticsearch")
        raise HTTPException(status_code=503, detail="Service is unreachable")

    return es_client


@search_router.get(
    "/",
    response_model=GlobalSearchResponse,
    summary="Global search"
)
@limiter.limit("20/minute")
async def global_search(
        request: Request,
        q: str = Query(..., description="Query string for the search"),
        es_client=Depends(get_es_client)
):
    """
    Global search endpoint, that performs a multi-index search using a multi_match query.
    Matches in the title have a higher score.
    Fuzzy matching is enabled to return similar results as well.
    The results are grouped by index.

    - q: The search query string.
    - Response body: A JSON object with grouped search results, each key represents the source index.
    """
    s = AsyncSearch(using=es_client, index=settings.global_search_indexes).query(
        "multi_match",
        query=q,
        fields=["title^2", "content"],
        fuzziness="AUTO"
    )

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

    logger.info(f"Global search succeeded, returning results from {len(result)} indexes")
    return GlobalSearchResponse(results=result)


@search_router.get("/service/{service_name}/")
@limiter.limit("20/minute")
async def search_by_service(request: Request,
                            service_name: str,
                            es_client=Depends(get_es_client)
                            ):
    """Service-specific search endpoint."""
    if service_name not in VALID_SERVICES:
        logger.error(f"Invalid service name attempted: {service_name}")
        raise HTTPException(status_code=400, detail=f"Invalid service name: {service_name}")

    logger.info(f"Search for {service_name} requested")
    return {"message": f"Search for service: {service_name} is working"}


@search_router.get("/suggestions/")
@limiter.limit("20/minute")
async def get_suggestions(request: Request, es_client=Depends(get_es_client)):
    """Endpoint for search suggestions."""
    logger.info("Suggestions requested")
    return {"message": "Suggestions are working"}
