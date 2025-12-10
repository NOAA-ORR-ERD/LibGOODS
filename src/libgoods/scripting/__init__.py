"""
Assorted utilities needed for scripting
"""

import logging
import sys


def initialize_console_log(level="debug"):
    """
    Initializes the logger to simply log everything to the console (stdout)

    Likely what you want for scripting use

    :param level='debug': the level you want your log to show. options are,
                          in order of importance: "debug", "info", "warning",
                          "error", "critical"

    You will only get the logging messages at or above the level you set.

    """
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    level = levels[level.lower()]
    format_str = "%(levelname)s - %(module)8s - line:%(lineno)d - %(message)s"
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=format_str,
    )
