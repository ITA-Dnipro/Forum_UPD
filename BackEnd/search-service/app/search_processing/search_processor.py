import json
from typing import List

from elasticsearch_dsl import Q
from pydantic import BaseModel

from .search_query import generic_search
from ..config import logger, settings
from ..utils.generate_cache_key import generate_cache_key


class BaseSearchService:
    """
    Encapsulates common search logic and structure:
    - index_name: Name of the Elasticsearch index.
    - search_fields: Fields to search on.
    - build_filters: Subclasses override this to build query filters.
    - search: Performs search and returns response including pagination details.
    """
    index_name: str
    search_fields: List[str]

    async def search(self, es_client, redis_client, params: BaseModel):
        logger.info(f"Performing search on index: {self.index_name}")
        cache_key = generate_cache_key(f"{self.index_name}", params.model_dump())
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info(f"Returning cached {self.index_name} search results")
            return json.loads(cached)

        filters = self.build_filters(params)
        total_records, records_list = await generic_search(
            es_client=es_client,
            index_name=self.index_name,
            query=params.query,
            filters=filters,
            sort_by=params.sort_by,
            search_fields=self.search_fields,
            sort_order=params.sort_order,
            page=params.page,
            page_size=params.page_size
        )
        result = {
            "total_records": total_records,
            "page": params.page,
            "page_size": params.page_size,
            "records_list": records_list
        }
        await redis_client.set(cache_key, json.dumps(result), ex=120)
        return result

    def build_filters(self, params) -> List[Q]:
        """
        Default implementation. Subclasses override to add custom filters.
        """
        return []


class EventSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving events from Elasticsearch."""
    index_name = settings.EVENTS_INDEX
    search_fields = ["title^2", "content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.category:
            filters.append(
                Q(
                    "nested",
                    path="categories",
                    query=Q("terms", **{
                        "categories.name": params.category})
                )
            )
        if params.event_type:
            filters.append(Q("term", type=params.event_type))
        if params.event_status:
            filters.append(Q("term", status=params.event_status))
        if params.location:
            filters.append(Q("term", location=params.location))
        if params.date_from:
            filters.append(Q("range", date={"gte": params.date_from}))
        return filters


class BlogPostSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving blog posts from Elasticsearch."""
    index_name = settings.FORUM_BLOG_POSTS_INDEX
    search_fields = ["title^2", "content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.author_id is not None:
            filters.append(Q("term", author_id=params.author_id))
        if params.category:
            filters.append(
                Q(
                    "nested",
                    path="categories",
                    query=Q("terms", **{
                        "categories.name": params.category})
                )
            )
        if params.tag:
            filters.append(
                Q("nested", path="tags", query=Q("terms", **{"tags.name": params.tag}))
            )
        if params.created_from:
            filters.append(Q("range", created_at={"gte": params.created_from}))
        return filters


class BlogCommentSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving blog comments from Elasticsearch."""
    index_name = settings.FORUM_BLOG_COMMENTS_INDEX
    search_fields = ["content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.author_id:
            filters.append(Q("term", author_id=params.author_id))
        if params.created_from:
            filters.append(Q("range", created_at={"gte": params.created_from}))
        return filters


class QuestionSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving questions from Elasticsearch."""
    index_name = settings.FORUM_QUESTIONS_INDEX
    search_fields = ["title^2", "content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.author_id:
            filters.append(Q("term", author_id=params.author_id))
        if params.status:
            filters.append(Q("term", status=params.status))
        if params.created_from:
            filters.append(Q("range", created_at={"gte": params.created_from}))
        return filters


class QuestionAnswerSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving question answers from Elasticsearch."""
    index_name = settings.FORUM_QUESTION_ANSWERS_INDEX
    search_fields = ["content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.author_id:
            filters.append(Q("term", author_id=params.author_id))
        if params.created_from:
            filters.append(Q("range", created_at={"gte": params.created_from}))
        return filters


class NewsSearchProcessor(BaseSearchService):
    """Search processor for filtering and retrieving news articles from Elasticsearch."""
    index_name = settings.NEWS_ARTICLES_INDEX
    search_fields = ["title^2", "content"]

    def build_filters(self, params) -> List[Q]:
        filters: List[Q] = []
        if params.published_from:
            filters.append(Q("range", published_at={"gte": params.published_from}))
        return filters
