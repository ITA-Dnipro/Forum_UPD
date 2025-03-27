from datetime import date
from typing import Optional, List, Set, ClassVar
from pydantic import BaseModel, Field, model_validator

from app.utils.enums import (
    SortOrder,
    EventType,
    EventStatus,
    QuestionStatus
)


class CommonParamsMixin(BaseModel):
    """Common pagination and sort order parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of results per page")
    sort_order: SortOrder = Field(default=SortOrder.desc, description="Sort order: 'asc' or 'desc'")
    include_suggestions: Optional[bool] = Field(False, description="Include search suggestions")
    query: Optional[str] = Field(default=None, description="Search query", min_length=2, max_length=200)


class SortByValidatorMixin(BaseModel):
    """
    Mixin that validates a 'sort_by' field against allowed fields.
    """
    sort_by: Optional[str] = None
    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = set()

    @model_validator(mode="after")
    def validate_sort_by(self):
        if self.sort_by is not None and self.sort_by not in self.ALLOWED_SORT_FIELDS:
            raise ValueError(f"Invalid sort_by field: {self.sort_by}. "
                             f"Allowed values: {self.ALLOWED_SORT_FIELDS}")
        return self


class EventSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching events."""
    category: Optional[List[str]] = Field([], description="List of categories to filter events by")
    event_type: Optional[EventType] = Field(default=None, description="Filter by the type of event")
    event_status: Optional[EventStatus] = Field(default=None, description="Status of the event")
    location: Optional[str] = Field(default=None, description="Filter events by location")
    date_from: Optional[date] = Field(default=None, description="Filter events occurring after this date (YYYY-MM-DD)")
    date_to: Optional[date] = Field(None, description="Filter events occurring after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field(default="date", description="Field to sort results by (default: date)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"date"}


class BlogPostSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching blog posts."""
    author_id: Optional[int] = Field(None, description="Filter by author ID")
    category: Optional[List[str]] = Field([], description="Blog post categories")
    tag: Optional[List[str]] = Field([], description="Blog post tags")
    created_from: Optional[date] = Field(None, description="Filter blog posts created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"likes_count", "created_at"}


class BlogCommentSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching blog comments."""
    author_id: Optional[str] = Field(None, description="Filter by comment author's ID")
    created_from: Optional[date] = Field(None, description="Filter comments created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"likes_count", "dislikes_count", "created_at"}


class QuestionSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching questions."""
    author_id: Optional[str] = Field(None, description="Filter by question author's ID")
    status: Optional[QuestionStatus] = Field(None, description="Filter by question status")
    created_from: Optional[date] = Field(None, description="Filter questions created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("views_count", description="Field to sort results by (default: views_count)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"views_count", "likes_count", "created_at"}


class QuestionAnswerSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching question answers."""
    author_id: Optional[str] = Field(None, description="Filter by answer author's ID")
    created_from: Optional[date] = Field(None, description="Filter answers created after this date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field("likes_count", description="Field to sort results by (default: likes_count)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"likes_count", "dislikes_count", "created_at"}


class NewsSearchParams(CommonParamsMixin, SortByValidatorMixin):
    """Parameters for searching news articles."""
    published_from: Optional[date] = Field(
        None, description="Filter news articles published after this date (YYYY-MM-DD)"
    )
    sort_by: Optional[str] = Field("published_at", description="Field to sort results by (default: published_at)")

    ALLOWED_SORT_FIELDS: ClassVar[Set[str]] = {"published_at"}
