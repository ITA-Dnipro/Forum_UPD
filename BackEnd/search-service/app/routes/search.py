import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import logger

search_router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

load_dotenv()

VALID_SERVICES = os.getenv("VALID_SERVICES", "").split(",") if os.getenv("VALID_SERVICES") else []


def get_es_client(request: Request):
    """Retrieves the Elasticsearch client from the FastAPI app state."""
    es_client = getattr(request.app.state, "es_client")

    if not es_client.ping():
        logger.error("Failed to reach Elasticsearch")
        raise HTTPException(status_code=503, detail="Service is unreachable")

    return es_client


@search_router.get("/")
@limiter.limit("20/minute")
async def global_search(request: Request, es_client=Depends(get_es_client)):
    """Global search endpoint."""
    logger.info("Global search requested")
    return {"message": "Global search is working"}


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
