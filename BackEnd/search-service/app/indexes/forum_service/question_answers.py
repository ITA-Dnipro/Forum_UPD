from elasticsearch_dsl import (
    Date,
    Integer,
    Keyword,
    Text,
    AsyncDocument
)

from ...config import settings


class QuestionAnswerDocument(AsyncDocument):
    """Document representing a question answer."""
    id = Keyword()
    author_id = Keyword()
    author_name = Text()

    content = Text(analyzer='standard')

    likes_count = Integer()
    dislikes_count = Integer()

    created_at = Date()

    class Index:
        name = settings.FORUM_QUESTION_ANSWERS_INDEX
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
