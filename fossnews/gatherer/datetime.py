from datetime import datetime, timezone
from enum import Enum
from time import mktime, struct_time


class DateTimeFormats(Enum):
    RFC822 = '%a, %d %b %Y %H:%M:%S %z'
    ISO8601 = '%Y-%m-%dT%H:%M:%S%z'


def to_datetime(dt: datetime | struct_time | str, fmt: str = DateTimeFormats.RFC822.value) -> datetime:
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, struct_time):
        return datetime.fromtimestamp(mktime(dt), timezone.utc)
    elif isinstance(dt, str):
        return datetime.strptime(dt, fmt)
    else:
        raise TypeError(f'Argument `dt` must be `datetime`, `struct_time` or `str`; got `{type(dt).__name__}`')


def format_datetime(dt: datetime | struct_time | str, fmt: str = DateTimeFormats.RFC822.value) -> str:
    """
    Format datetime as ISO 8601 string.

    :param datetime dt: date and time.
    :param str fmt: format string.
    :return: date and time in ISO 8601 format.
    """
    return to_datetime(dt, fmt=fmt).strftime(DateTimeFormats.ISO8601.value)
