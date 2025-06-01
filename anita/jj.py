"""Some utilities around JavaScript Object Notation (JSON)."""

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Union


def dumps(x: list | dict) -> str:  # noqa: C901
    """Produce denser JSON rendering than json.dumps(indent=4).

    Supports nested lists and dicts. Tuples and sets are rendered as list.
    Element types can be int, float and str. Datetime, date and Decimal are rendered as str.
    Compatibility with json.loads, when only list, dict, int, float and str are in the game.
    All other element types raise ValueError.

    >>> print(dumps({"a": 1, "b": [2, 3], "c": {"d": 4}}))
    {
        "a": 1,
        "b": [2, 3],
        "c": {"d": 4}
    }
    >>> print(dumps({"a": 1, "b": [2, 3], "c": {"d": 4, "e": 5}}))
    {
        "a": 1,
        "b": [2, 3],
        "c": {"d": 4, "e": 5}
    }
    >>> print(dumps({"a": 1, "b": [2, 3], "c": {"d": 4, "e": [5, 6]}}))
    {
        "a": 1,
        "b": [2, 3],
        "c": {
            "d": 4,
            "e": [5, 6]
        }
    }
    """

    def _is_atomic(x: object) -> bool:  # prepare for datetime etc.
        if x is None:
            return True
        if isinstance(x, (dict, list, set, tuple)):
            return False
        if not isinstance(x, (int, float, str, datetime, date, Decimal)):
            raise TypeError(x.__class__.__name__)
        return True

    def _is_compound_of_atomic(o):
        if isinstance(o, (list, set, tuple)):
            return all(_is_atomic(v) for v in o)
        if isinstance(o, dict):
            return all(_is_atomic(v) for v in o.values())
        return False

    def _is_oneliner(x) -> bool:
        return _is_atomic(x) or _is_compound_of_atomic(x)

    def _j(x, indent="", is_element=False) -> str:
        next_ = indent + "    "
        cond = "" if is_element else indent
        if _is_oneliner(x):
            if isinstance(x, (set, tuple)):
                x = list(x)
            # cf. https://stackoverflow.com/a/26195385/3991164 re. default=
            return cond + json.dumps(x, default=str)
        if isinstance(x, dict):
            return "\n".join(
                [f"{cond}{{", ",\n".join([f'{next_}"{k}": {_j(v, next_, True)}' for k, v in x.items()]), indent + "}"]
            )
        if isinstance(x, (list, set, tuple)):
            return "\n".join([f"{cond}[", ",\n".join([_j(v, next_, False) for v in x]), indent + "]"])
        raise TypeError(f"Unsupported type: {type(x)}")

    return _j(x)  # hide additional arguments


def jpath(o: dict | list, path: str) -> Any:
    """Dive in nested dicts and lists of known structure, like API returns.
    Access nested components with a simple path like "data/0/name" instead of
    consecutive indexing like ["data"][0]["name"].
    This does NOT dive into strings by index, just because strings are indexable
    like lists, because this is usually NOT what you want.

    >>> j = {"data": [{"name": "Alice"}, {"name": "Bob"}]}
    >>> jpath(j, "data/0/name")
    'Alice'
    >>> jpath(j, "data/1/name")
    'Bob'
    >>> jpath(j, "data/2/name")
    Traceback (most recent call last):
        ...
    ValueError: Invalid path '2/name' for remaining object [{'name': 'Alice'}, {'name': 'Bob'}]
    >>> jpath(j, "data/name")
    Traceback (most recent call last):
        ...
    ValueError: Invalid path 'name' for remaining object [{'name': 'Alice'}, {'name': 'Bob'}]
    >>> jpath(j, "data/0")
    {'name': 'Alice'}
    >>> jpath(j, "data/0/name/0")
    Traceback (most recent call last):
        ...
    ValueError: Invalid path '0' for remaining object 'Alice'
    """
    steps = path.split("/")
    try:
        for i, step in enumerate(steps):
            # convert to numeric only if next level is list
            o = o[int(step)] if step.isdigit() and isinstance(o, list) else o[step]  # type: ignore[index]
        return o
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Invalid path '{'/'.join(steps[i:])}' for remaining object {o!r}") from e  # type: ignore


class Accessor:
    """A simple jpath and dot-notation accessor for nested dicts and lists.
    - jpath allows to access nested components with a simple path like "data/0/name"
    - dot-notation will only work one level, because base object data is returned as-is
      and not wrapped in another Accessor.

    >>> obj = Accessor({"a": 1, "b": {"c": 2}})
    >>> obj.a
    1
    >>> obj.jpath("b/c")
    2
    """

    def __init__(self, j: list | dict) -> None:
        """Initialize the Accessor with a list or dict.

        >>> obj = Accessor({"a": 1, "b": {"c": 2}})
        >>> # spot-checking
        >>> obj.a
        1
        >>> obj = Accessor([{"a": 1}, {"b": 2}])
        >>> # spot-checking
        >>> obj.jpath("0/a")
        1

        >>> obj = Accessor(17)
        Traceback (most recent call last):
        ...
        TypeError: Accessor: expected list or dict, got 'int'
        """
        if not isinstance(j, (list, dict)):
            raise TypeError(f"Accessor: expected list or dict, got {type(j).__name__!r}")
        self.j = j

    def __getattr__(self, __name: str, /) -> Any:
        """Access the nested data structure like a dict, but with dot notation.
        Works only one level deep, because the base object is returned as-is,
        not wrapped in another Accessor.

        >>> ob = Accessor({"a": 1, "b": {"c": 2}})
        >>> ob.a
        1
        >>> ob.b.c
        Traceback (most recent call last):
        ...
        AttributeError: 'dict' object has no attribute 'c'
        """
        if __name in self.j:
            return self.j[__name]  # type: ignore[return-value]
        raise AttributeError(__name)

    def jpath(self, path: str) -> Any:
        """Dive in nested dicts and lists of known structure, like API returns.
        Access nested components with a simple path like "data/0/name" instead of
        consecutive indexing like ["data"][0]["name"].

        >>> ob = Accessor({"a": 1, "b": {"c": 2}})
        >>> ob.a
        1
        >>> ob.jpath("b/c")
        2
        >>> ob.jpath("b/0")
        Traceback (most recent call last):
        ...
        ValueError: Invalid path '0' for remaining object {'c': 2}
        """
        o = self.j
        steps = path.split("/")
        try:
            for i, step in enumerate(steps):
                # convert to numeric only if next level is list or a string
                o = o[int(step)] if step.isdigit() and isinstance(o, (list, str)) else o[step]  # type: ignore[index]
            return o
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Invalid path '{'/'.join(steps[i:])}' for remaining object {o!r}") from e  # type: ignore


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
