from elasticsearch_dsl import (
    Document,
    Date,
    Integer,
    Keyword,
    Text
)


class QuestionAnswerDocument(Document):
    """Document representing a question answer."""
    id = Keyword()
    author_id = Keyword()
    author_name = Text()

    content = Text(analyzer='standard')

    likes_count = Integer()
    dislikes_count = Integer()

    created_at = Date()

    class Index:
        name = 'question_answers'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
