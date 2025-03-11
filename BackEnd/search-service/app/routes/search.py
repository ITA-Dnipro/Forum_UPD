import logging

from fastapi import APIRouter, Depends, Request, HTTPException

search_router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_es_client(request: Request):
    """Retrieves the Elasticsearch client from the FastAPI app state."""
    es_client = getattr(request.app.state, "es_client")

    if not es_client.ping():
        logger.error(f"Failed to reach Elasticsearch")
        raise HTTPException(status_code=503, detail="Service is unreachable")

    return es_client


@search_router.get("/")
async def global_search(es_client=Depends(get_es_client)):
    """Global search endpoint that uses the shared Elasticsearch client."""
    return {"message": "Global search is working"}


@search_router.get("/{service_name}")
async def search_by_service(service_name: str, es_client=Depends(get_es_client)):
    """Service-specific search endpoint."""
    return {"message": f"Search for service: {service_name} is working"}


@search_router.get("/suggestions")
async def get_suggestions(es_client=Depends(get_es_client)):
    """Endpoint for search suggestions."""
    return {"message": "Suggestions are working"}
