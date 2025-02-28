from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.cassandra import async_init_cassandra
from app.routes import posts, questions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

origins = settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def register_routers(app: FastAPI):
    app.include_router(posts.router, prefix="/posts", tags=["Posts"])
    app.include_router(questions.router, prefix="/questions", tags=["Questions"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Cassandra...")
    await async_init_cassandra()  
    
    from app.utils.migrations import run_migrations
    logger.info("Running migrations...")
    await run_migrations() 
    
    logger.info("Running database seed...")
    from app.utils.seed_data import seed_database
    await seed_database()  

    logger.info("Seed process completed.")

    

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "status": "running"
    }

register_routers(app)