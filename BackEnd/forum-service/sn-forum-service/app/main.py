from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.cassandra import async_init_cassandra, basic_init_cassandra, get_session, refresh_metadata
from app.routes import posts, categories, tags
import logging
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Forum Microservice API",
    description="A microservice-based API for managing blog posts, categories, tags, comments, and saved posts in a forum system.",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs",  
    redoc_url="/redoc"  
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

def register_routers(app: FastAPI):
    app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
    app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
    app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Cassandra basic connection...")
    session = await basic_init_cassandra()
    
    logger.info("Running migrations...")
    from app.utils.migrations import run_migrations
    await run_migrations()
    
    logger.info("Refreshing metadata and registering UDT types...")
    await refresh_metadata()
    
    from app.services.cassandra import register_user_types
    await register_user_types(session.cluster)
    
    logger.info("Running database seed...")
    from app.utils.seed_data import seed_database
    await seed_database()
    
    logger.info("Startup completed successfully.")

@app.get(
    "/",
    summary="Root Endpoint",
    description="Returns a welcome message for the Forum Microservice API.",
    response_description="A simple JSON response with a welcome message and status."
)
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "status": "running"
    }

register_routers(app)