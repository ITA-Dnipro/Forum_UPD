from elasticsearch_dsl import (
    Document,
    Date,
    Text,
    Keyword
)


class NewsArticleDocument(Document):
    """Document representing a news article."""
    id = Keyword()

    title = Text(analyzer="standard")
    content = Text(analyzer="standard")

    published_at = Date()

    class Index:
        name = "news_articles"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
