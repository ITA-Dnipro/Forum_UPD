from datetime import datetime
from zoneinfo import ZoneInfo

def to_local_time(datetime: datetime):
    return str(datetime.astimezone(ZoneInfo("Europe/Kyiv"))) 