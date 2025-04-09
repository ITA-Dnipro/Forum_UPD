from datetime import datetime
from zoneinfo import ZoneInfo

def to_local_time(datetime: datetime):
    return datetime.astimezone(ZoneInfo("Europe/Kyiv")) 

def moderation_time_to_str(hours: float):
    minutes = round((hours - int(hours)) * 60, 0)
    return str(f'{int(hours)} год та {minutes} хв')


def update_time_to_str(time: datetime):
    print('time: ', time, type(time))
    local_time = to_local_time(time)
    return str(local_time.strftime("%Y-%m-%d %H:%M"))