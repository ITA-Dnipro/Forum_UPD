from elasticsearch_dsl import (
    Date,
    Text,
    Keyword,
    AsyncDocument
)

from ...config import settings


class NewsArticleDocument(AsyncDocument):
    """Document representing a news article."""
    id = Keyword()

    title = Text(analyzer="standard")
    content = Text(analyzer="standard")

    published_at = Date()

    class Index:
        name = settings.news_articles_index
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
