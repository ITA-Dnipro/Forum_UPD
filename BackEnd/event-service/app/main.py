from fastapi import FastAPI, HTTPException
import uvicorn
from routes.events.urls import router as events_router
from routes.participants.urls import router as participants_router

app = FastAPI(title="Event Microservice")

app.include_router(events_router)
app.include_router(participants_router)

@app.get("/", summary="Entry point to Event Service")
def read_root():
    return {"message": "Welcome to Event Microservice!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)