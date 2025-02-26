from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.cassandra import init_cassandra
from app.routes import posts, questions

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("init casandra")

    init_cassandra() 
    
    from app.utils.migrations import run_migrations
    run_migrations()
    print("Додаток працює, запускаємо seed")

    from app.utils.seed_data import seed_database
    seed_database()

    print("seed завершено")

    

app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "status": "running"
    }