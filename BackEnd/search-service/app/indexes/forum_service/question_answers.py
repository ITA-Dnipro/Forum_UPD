from elasticsearch_dsl import (
    Date,
    Integer,
    Keyword,
    Text,
    AsyncDocument,
    Boolean,
)

from ...config import settings


class QuestionAnswerDocument(AsyncDocument):
    """Document representing a question answer."""
    id = Keyword()
    author_id = Keyword()
    question_id = Keyword()

    content = Text(analyzer='standard')

    likes_count = Integer()
    dislikes_count = Integer()
    is_accepted = Boolean()

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
