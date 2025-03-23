from typing import Optional, List

from pydantic import BaseModel, Field


class EventSearchParams(BaseModel):
    """Parameters for searching events."""
    query: Optional[str] = Field(default=None, description="Search query for event title or description")
    category: Optional[List[str]] = Field([], description="List of categories to filter events by")
    event_type: Optional[str] = Field(default=None, description="Filter by the type of event")
    event_status: Optional[str] = Field(default=None, description="Status of the event")
    location: Optional[str] = Field(default=None, description="Filter events by location")
    date_from: Optional[str] = Field(default=None, description="Filter events occurring after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field(default="date", description="Field to sort results by (default: date)")


class BlogPostSearchParams(BaseModel):
    """Parameters for searching blog posts."""
    query: Optional[str] = Field(None, description="Search query for blog post titles and content")
    author_id: Optional[int] = Field(None, description="Filter by author ID")
    category: Optional[List[str]] = Field([], description="Blog post categories")
    tag: Optional[List[str]] = Field([], description="Blog post tags")
    created_from: Optional[str] = Field(None, description="Filter blog posts created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")


class BlogCommentSearchParams(BaseModel):
    """Parameters for searching blog comments."""
    query: Optional[str] = Field(None, description="Search query for blog comment content")
    author_id: Optional[str] = Field(None, description="Filter by comment author's ID")
    created_from: Optional[str] = Field(None, description="Filter comments created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")


class QuestionSearchParams(BaseModel):
    """Parameters for searching questions."""
    query: Optional[str] = Field(None, description="Search query for question titles and content")
    author_id: Optional[str] = Field(None, description="Filter by question author's ID")
    status: Optional[str] = Field(None, description="Filter by question status")
    created_from: Optional[str] = Field(None, description="Filter questions created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("views_count", description="Field to sort results by (default: views_count)")


class QuestionAnswerSearchParams(BaseModel):
    """Parameters for searching question answers."""
    query: Optional[str] = Field(None, description="Search query for answer content")
    author_id: Optional[str] = Field(None, description="Filter by answer author's ID")
    created_from: Optional[str] = Field(None, description="Filter answers created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")


class NewsSearchParams(BaseModel):
    """Parameters for searching news articles."""
    query: Optional[str] = Field(None, description="Search query for news article titles and content")
    published_from: Optional[str] = Field(None,
                                          description="Filter news articles published after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("published_at", description="Field to sort results by (default: published_at)")
