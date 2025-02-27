# app/routes/posts.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/posts",  
    tags=["Posts"]    
)

@router.get("/")
async def get_posts():
    return {"message": "List of posts"}