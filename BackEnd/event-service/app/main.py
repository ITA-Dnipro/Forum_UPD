from fastapi import FastAPI, HTTPException
import uvicorn
from routes import events#, registration
from database import engine, Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(title="Event Microservice", on_startup=[init_models])

app.include_router(events.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Event Microservice!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)