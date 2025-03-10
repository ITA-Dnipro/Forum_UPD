import logging

from fastapi import APIRouter

search_router = APIRouter()

logger = logging.getLogger(__name__)


@search_router.get("/")
async def global_search():
    """Placeholder for global search endpoint."""
    return {"message": "Global search is working"}


@search_router.get("/{service_name}")
async def search_by_service(service_name: str):
    """Placeholder for service-specific search endpoint."""
    return {"message": f"Search for service: {service_name} is working"}


@search_router.get("/suggestions")
async def get_suggestions():
    """Placeholder for suggestions endpoint."""
    return {"message": "Suggestions are working"}
