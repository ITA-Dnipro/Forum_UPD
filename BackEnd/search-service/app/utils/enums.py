from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class EventType(str, Enum):
    online = "online"
    offline = "offline"
    auction = "auction"


class EventStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class QuestionStatus(str, Enum):
    open = "open"
    closed = "closed"
    resolved = "in progress"
