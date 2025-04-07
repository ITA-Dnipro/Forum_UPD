from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Utils & Validation API",
    description="API for validation fields and other utils",
    version="1.0.0"
)

app.include_router(router, prefix="/api")
