from elasticsearch_dsl import (
    Date,
    Integer,
    Keyword,
    Text,
    AsyncDocument
)

from ...config import settings


class QuestionDocument(AsyncDocument):
    """Document representing a question."""
    id = Keyword()
    author_id = Keyword()

    title = Text(analyzer='standard')
    content = Text(analyzer='standard')

    status = Keyword()
    likes_count = Integer()
    views_count = Integer()

    created_at = Date()
    updated_at = Date()

    class Index:
        name = settings.forum_questions_index
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
