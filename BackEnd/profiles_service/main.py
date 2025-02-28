from fastapi import FastAPI
import uvicorn
from routers import profiles, categories, regions

app = FastAPI(root_path="/api/v1")
app.include_router(profiles.router, prefix="/profiles")
app.include_router(categories.router, prefix="/categories")
app.include_router(regions.router, prefix="/regions")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
