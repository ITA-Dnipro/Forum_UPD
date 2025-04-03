from enum import Enum

class StatusEnum(Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"
    
class TypeEnum(Enum):
    online = "online"
    offline = "offline"
    auction = "auction"