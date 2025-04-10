import datetime


def convert_time(microseconds_since_midnight):
    """
    Convert an integer representing the number of microseconds since midnight
    to a time object.
    """
    seconds_since_midnight = microseconds_since_midnight / 1e6
    hours, remainder = divmod(seconds_since_midnight, 3600)
    minutes, seconds = divmod(remainder, 60)
    return datetime.time(int(hours), int(minutes), int(seconds))