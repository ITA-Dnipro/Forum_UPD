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


class EventDocument(AsyncDocument):
    """Document representing an event."""
    id = Keyword()
    organizer_id = Integer()

    title = Text(analyzer="standard")
    content = Text(analyzer="standard")

    categories = Nested(Category)
    type = Keyword()
    status = Keyword()

    location = Keyword()
    image = Keyword()
    available_slots = Integer()
    max_participants = Integer()

    date = Date()
    starting_time = Date()

    class Index:
        name = settings.events_index
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }

    @classmethod
    def get_index_name(cls):
        return cls.Index.name
