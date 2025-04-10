import datetime


def process_timestamp_field(field, key):
    """
    Converts a timestamp field into a datetime object if it is a dict
    with a "$date" key. Otherwise, returns the field as-is.
    """
    timestamp_sec = field[key] / 1000.0
    return datetime.datetime.fromtimestamp(timestamp_sec, tz=datetime.timezone.utc)
