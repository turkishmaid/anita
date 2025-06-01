"""This module provides functions to prevent a module from being run as a script."""


def not_an_app():
    """Fail the execution.
    useful when you have something that you don't want to run as a script
    (maybe because initialization is costy or potentially malicious).

    >>> not_an_app()
    Traceback (most recent call last):
        ...
        raise SystemExit(1)
    SystemExit: 1
    """
    print("\n\nThis is not an executable program.\n\n")
    raise SystemExit(1)


def not_a_script() -> None:
    """Prevent a module from being run as a script.

    >>> not_a_script()
    Traceback (most recent call last):
        ...
        raise SystemExit(1)
    SystemExit: 1

    """
    kilroy = r"""

                              ,,,
                             (o o)
-._,--------------._,----ooO--(…)--Ooo--._,----

                               This is a module, not a script.


"""
    print(kilroy)  # noqa: T201
    raise SystemExit(1)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
