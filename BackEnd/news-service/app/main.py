# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield  
    
app = FastAPI(lifespan=lifespan)


app.include_router(router, prefix="/api")