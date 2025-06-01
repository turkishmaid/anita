"""Manage paths respecting user privacy."""

from pathlib import Path


def safe(s: str | Path) -> str:
    """Remove $HOME (containing personal data) from a path."""
    s = str(s)
    home = str(Path.home())
    if s.startswith(home):
        return s.replace(home, "~")
    return s
