"""All things date and time."""

from __future__ import annotations
from datetime import datetime, date, timezone, UTC
from typing import Union
import re


def utcnow() -> datetime:
    """Get the current UTC time as a timezone-aware datetime object."""
    return datetime.now(tz=UTC)


def sara_date(s: str | datetime | date | None = None) -> str:
    """Format a Sara-style short date.

    Year A=2010 .. L=2021 + month 1-9ABC, C=December + 2 digit day.
    The format is sortable, but saves 60% space in print.
    Date's and short strings will be formatted as day-only: LB16
    When time is supplied, it will be used, too: LB16-0706

    @param s: ISO date string like "2010-12-24" or date/datetime
    @return: shorter representation like "AC24"

    >>> sara_date("2010-12-24")
    'AC24'
    >>> sara_date("2010-12-24T07:06")
    'AC24-0706'
    >>> sara_date(date(1971, 2, 24))  # TODO this should fail for years < 2000
    Traceback (most recent call last):
        ...
    AssertionError: Year must be >= 2000, got 1971
    """
    Y2K = 2000
    base46 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if s is None:
        s = utcnow().isoformat()
    if isinstance(s, (date, datetime)):
        s = s.isoformat()
    assert int(s[0:4]) >= Y2K, f"Year must be >= {Y2K}, got {s[0:4]}"
    yr = base46[int(s[0:4]) - Y2K]
    mnth = base46[int(s[5:7])]
    day = s[8:10]
    if len(s) == 10:  # noqa: PLR2004
        return f"{yr}{mnth}{day}"
    hr_ = s[11:13]
    min_ = s[14:16]
    return f"{yr}{mnth}{day}-{hr_}{min_}"


def from_sara_date(sd: str) -> date:
    """Convert a Sara-style short date back to a date object."""
    yyyy = ord(sd[0]) - ord("A") + 2010 if sd[0] >= "A" else int(sd[0]) + 2000
    mm = ord(sd[1]) - ord("A") + 10 if sd[1] >= "A" else int(sd[1])
    dd = int(sd[2:])
    return date(year=yyyy, month=mm, day=dd)


def split_seconds(seconds: float) -> str:
    """Funny stuff: render a duration like 5d 10m 3.5s."""
    secs = seconds % 60
    seconds //= 60
    seconds = int(round(seconds, 0))
    mins = seconds % 60
    seconds //= 60
    hrs = seconds % 24
    seconds //= 24
    days = seconds
    a = []
    if days:
        a.append(f"{days}d")
    if hrs:
        a.append(f"{hrs}h")
    if mins:
        a.append(f"{mins}m")
    if secs >= 0.1:
        a.append(f"{secs:0.1f}s")
    if a:
        return " ".join(a)
    return "no time"


def check_date(s: str) -> bool:
    """Check if a string is a valid date in the format YYYY-MM-DD."""
    return bool(re.match(r"^[12][0-9]{3}-[0-9]{2}-[0-9]{2}$", s) and s[:2] in ["19", "20"])


def number62(n: int, pad: int = 3) -> str:
    """Very short string representation of an integer.

    pad=3 suitable for counting days from Jan 1, 1900.
    Kudos https://stackoverflow.com/questions/2267362#28666223

    :param n: an integer
    :param pad: result padded to that length with zeroes
    :return: strictly ascending base-62 representation of n
    """
    if n == 0:
        return "0".rjust(pad, "0")
    digits = []
    while n:
        digits.append(int(n % 62))
        n //= 62
    a = []
    for d in digits[::-1]:
        a.append("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"[d])
    return "".join(a).rjust(pad, "0")


def date62(iso: str) -> str:
    """Transform date or datetime isoformat to a very short, strictly ascending string representation.

    :param iso: someting like 2022-04-16...
    :return: 3-digit base 3 representation of days elapsed since Jan 1, 1900
    """
    assert check_date(iso)
    d0 = date.fromisoformat(iso)
    dd = (d0 - date(1900, 1, 1)).days
    return number62(dd, pad=3)


def datetime_from_date(date_: Union[str, date]) -> datetime:
    """Convert a date or date string to a datetime object at midnight."""
    # https://stackoverflow.com/a/1937636/3991164
    if isinstance(date_, str):
        date_ = date.fromisoformat(date_)
    assert isinstance(date_, date)
    return datetime.combine(date_, datetime.min.time())


def utcage(ts_utc: datetime | float) -> int:
    """How many seconds ago was this."""
    if isinstance(ts_utc, (int, float)):
        ts_utc = datetime.fromtimestamp(ts_utc, UTC)
    return int((utcnow() - ts_utc.replace(tzinfo=UTC)).total_seconds())
