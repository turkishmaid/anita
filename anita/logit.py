"""Write stack, exceptions and the like to the logfile in a way I like it."""

import logging
from typing import Callable
import sys
import traceback
import subprocess

logger = logging.getLogger("anita.logit")


def full_stack() -> str:
    r"""Return the full stack trace as a string.
    
    cf. https://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python

    >>> s = full_stack()
    >>> isinstance(s, str)
    True
    >>> s.startswith("Traceback (most recent call last):")
    True
    >>> s.endswith("full_stack()\n")
    True
    """
    exc = sys.exc_info()[0]
    if exc is not None:
        f = sys.exc_info()[-1].tb_frame.f_back   # type: ignore
        stack = traceback.extract_stack(f)
    else:
        stack = traceback.extract_stack()[:-1]
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        stackstr += "  " + traceback.format_exc()[len(trc) :]
    return stackstr


def log_exception(e: BaseException, log_func: Callable[[str], None] = logger.error) -> None:
    """Neatly log the exception.
    Optionally, pass in a logger function to use, else my local logger's error() is used.
    TODO use last exception as default.
    """
    log_func("    +----------------------------------------------------------------------------------------")
    log_func("    |")
    log_func(f"    |        EXCEPTION ---> {e}")
    log_func("    |")
    log_func("    +----------------------------------------------------------------------------------------")
    log_func("    |")
    # expand line feeds in traceback output
    # note: lines end with line feeds, and may contain line feeds!
    ll = list("".join(traceback.format_exception(e)).split("\n"))
    for i, line in enumerate(ll):
        log_func(f"{i:3} |  {line}")


def log_df(log_func: Callable = logger.info) -> None:
    """Run "df -h ." and print output to the logs.
    Supposed to work on MacOS/Linux. Others: Let Copilot suggest some crazy stuff.
    Optionally, pass in a logger function to use, else my local logger's info() is used.
    """
    try:
        result = subprocess.run(["df", "-h", "."], capture_output=True, text=True, check=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if line:
                log_func(line)
    except subprocess.CalledProcessError as e:
        log_exception(e)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)

    # run a test to see if the log_exception() works
    try:
        1 / 0
    except ZeroDivisionError as e:
        log_exception(e)
