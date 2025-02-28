from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from app.services.cassandra import get_session
from app.schemas.post import PostCreate, PostResponse, PostList
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PostList])
async def list_posts(
):
    #just prescribed for the futurejust anonnced
    pass