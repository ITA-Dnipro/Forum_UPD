from typing import Dict, List

from pydantic import BaseModel


class GlobalSearchResultItem(BaseModel):
    """Model represents a single global search result."""
    id: str
    title: str
    content: str


class GlobalSearchResponse(BaseModel):
    """Response model grouping search results by index."""
    results: Dict[str, List[GlobalSearchResultItem]]
