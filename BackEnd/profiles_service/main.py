from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from routers import investors, categories, regions, images, startups

app = FastAPI(root_path="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(startups.router, prefix="/startup_profiles")
app.include_router(investors.router, prefix="/investor_profiles")
app.include_router(categories.router, prefix="/startup_categories")
app.include_router(regions.router, prefix="/regions")
app.include_router(images.router, prefix="/images")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
