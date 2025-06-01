"""Timer module providing utilities for measuring execution time of code blocks."""

from __future__ import annotations
from time import perf_counter, sleep  # noqa: F401
from typing import Self


class Timer:
    """Context handler to stopwatch stuff.

    >>> with Timer() as t:
    ...    pass # do stuff
    >>> sleep(0.01)  # <- not on the bill!
    >>> print(f"stuff  {t.read()}")
    stuff  [0.000 s]
    """

    def __init__(self) -> None:
        """Initialize the Timer."""
        self.elapsed: float = 0.0
        self.start: float = -1.0

    def __enter__(self) -> Self:
        """Start the Timer."""
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback) -> None:
        """Stop the Timer and calculate elapsed time."""
        self.elapsed = perf_counter() - self.start

    def reset(self) -> None:
        """Reset the Timer."""
        self.start = perf_counter()

    def read(self, *, raw: bool = False) -> float | str:
        """Read the elapsed time without stopping the Timer."""
        if self.elapsed:
            return self.elapsed if raw else f"[{self.elapsed:0.3f} s]"
        dt = perf_counter() - self.start
        return dt if raw else f"[{dt:0.3f} s]"


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
