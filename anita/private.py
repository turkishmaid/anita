#!/usr/bin/env python3
# pylint: disable=logging-fstring-interpolation,broad-exception-caught,unused-import

"""
Context free utility functions, --> based on the Python standard lib only. <--
Running this file as a script will run some doctests. Neat, isn't it?
"""

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, date, timezone
from decimal import Decimal
import json
from os import environ
from pathlib import Path
import re
import sys
from time import perf_counter, sleep
import traceback
from typing import Union, Any, Callable, Generator
import hashlib
import logging
import subprocess

logger = logging.getLogger("ganesha.pythonx")


def render_as_ascii_table(x: list[dict], fields: list[str] | None = None) -> list[str]:
    """Render table as list of strings, one per row."""
    resu: list[str] = []
    lens = defaultdict(int)
    if fields:
        for f in fields:
            lens[f] = 0
    for row in x:
        for f in row:
            lens[f] = max(lens[f], len(str(row[f])))
    last = dict.fromkeys(lens, " ")
    for row in x:
        a = []
        for f in lens:
            val = str(row[f]) if f in row else "-"
            if val == last[f]:
                val = " "
            else:
                last[f] = val
            a.append(val.ljust(lens[f], " "))
        resu.append(" | ".join(a))
    return resu


def replace_datetime(x: Any, first_call: bool = True) -> Any:
    """Replace date and datetime objects with their ISO format string representation.
    You will mostly rather use json.dump(o, default=str).
    Returns a copy of the list or dict passed as x with all occurrences of
    datetime or date replaced by their ISO format string representation.
    Made for json.dump, but there are better solutions.
    """
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if not isinstance(x, (list, dict)):
        return x
    if first_call:
        x = deepcopy(x)
    if isinstance(x, list):
        for i, _ in enumerate(x):
            x[i] = replace_datetime(x[i], first_call=False)
        return x
    if isinstance(x, dict):
        for k in x:
            x[k] = replace_datetime(x[k], first_call=False)
        return x
    # this will not dive into general objects
    return x


def hr_old(i: int) -> str:
    """Convert a integer data volume like 3485678 to a human readable format.

    >>> hr(3485678)
    '3.3 MB'
    >>> hr(17)
    '17'
    """
    K = 1024
    if i < K:
        return str(i)
    if i < K * K:
        return f"{i / K:0.1f} kB"
    if i < K * K * K:
        return f"{i / K / K:0.1f} MB"
    return f"{i / K / K / K:0.1f} GB"


def hr(i: float) -> str:
    """Convert a data volume like 3485678 to a human readable format.
    You may consider `humanize.naturalsize(i, binary=True)` instead.

    >>> hr(3485678)
    '3.3 MB'
    >>> hr(17)
    '17'
    """
    k = 1024
    units = ["", "kB", "MB", "GB", "TB", "PB"]

    # Find appropriate unit
    power = 0
    while i >= k and power < len(units) - 1:
        i /= k
        power += 1

    # Format appropriately
    if power == 0:
        return str(int(i))
    return f"{i:.1f} {units[power]}"


def shorten(s: str, l: int = 50) -> str:
    """Shorten a string to l characters, append ... if shortened."""
    if len(s) > l:
        s = s[: l - 3] + "..."
    return s


def partition_list(l, n) -> Generator[list]:
    """Partition a list into chunks of size n.
    cf. https://www.techiedelight.com/partition-list-python/ for details.
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]


def static_vars(**kwargs):
    """Support static variables in functions.

    Statics can be accessed via dot notation.
    cf. https://stackoverflow.com/a/279586/3991164

    :param kwargs: the static variables with an initial value
    :return: the decorated function

    >>> @static_vars(v=[])
    ... def func(s: Any) -> None:
    ...     func.v.append(s)
    >>> func(1)
    >>> func(2)
    >>> len(func.v)
    2
    """

    def decorate(func: Callable) -> Callable:
        """Decorate the function with static variables."""
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func

    return decorate


class classproperty:  # noqa: N801
    """A class property decorator to access class properties like instance properties.

    Don't use this. cf. https://stackoverflow.com/a/13624858
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


def choose(choices: list, default: int = 0) -> int:
    """Let the user choose from a list of choices, return the index of the choice."""
    assert default < len(choices)
    for i, c in enumerate(choices):
        print(f"{i:3d} - {c}")
    ch = input(f"choose from the above (default: {default}) ")
    ch = default if ch == "" else int(ch)
    print(f"--> using {choices[ch]}")  # noqa: T201
    return ch


def calculate_md5(file_path: Path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


