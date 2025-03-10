from fastapi import FastAPI, HTTPException
import uvicorn
from routes import events, registration
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Microservice")

app.include_router(events.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Event Microservice!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)