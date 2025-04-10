import datetime


def convert_date(days_since_epoch):
    """
    Convert an integer representing the number of days since 1970-01-01
    to a date object.
    """
    base_date = datetime.date(1970, 1, 1)
    return base_date + datetime.timedelta(days=days_since_epoch)