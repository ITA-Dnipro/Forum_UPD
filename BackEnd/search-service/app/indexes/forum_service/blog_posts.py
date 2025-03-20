from elasticsearch_dsl import (
    Date,
    Integer,
    Text,
    Keyword,
    Nested,
    InnerDoc,
    AsyncDocument
)

from ...config import settings


class Category(InnerDoc):
    """Document representing a category."""
    category_id = Integer()
    name = Keyword()


class Tag(InnerDoc):
    """Document representing a tag."""
    tag_id = Integer()
    name = Keyword()


class BlogPostDocument(AsyncDocument):
    """Document representing a blog post."""
    id = Keyword()
    author_id = Integer()

    title = Text(analyzer="standard")
    content = Text(analyzer="standard")

    likes_count = Integer()
    categories = Nested(Category)
    tags = Nested(Tag)

    images = Keyword(multi=True)
    created_at = Date()
    updated_at = Date()

    class Index:
        name = settings.FORUM_BLOG_POSTS_INDEX
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
