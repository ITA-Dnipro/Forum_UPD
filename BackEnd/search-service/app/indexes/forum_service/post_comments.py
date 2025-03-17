from elasticsearch_dsl import (
    Document,
    Date,
    Integer,
    Text,
    Keyword
)


class PostCommentDocument(Document):
    """Document representing a blog post comment."""
    id = Keyword()
    author_id = Keyword()

    content = Text(analyzer="standard")

    likes_count = Integer()
    dislikes_count = Integer()

    created_at = Date()

    class Index:
        name = "blog_comments"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
