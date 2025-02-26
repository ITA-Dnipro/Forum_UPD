# app/routes/posts.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_posts():
    return {"message": "List of posts"}
