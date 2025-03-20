from elasticsearch_dsl import (
    Date,
    Integer,
    Text,
    Keyword,
    AsyncDocument
)

from ...config import settings


class PostCommentDocument(AsyncDocument):
    """Document representing a blog post comment."""
    id = Keyword()
    author_id = Keyword()

    content = Text(analyzer="standard")

    likes_count = Integer()
    dislikes_count = Integer()

    created_at = Date()

    class Index:
        name = settings.forum_blog_comments_index
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
