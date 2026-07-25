"""
===========================================================
Deriv SDK

Logger

Provides structured logging for the SDK.

Version : 0.1.0
===========================================================
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logger(level: int = logging.INFO) -> None:
    """
    Configure the SDK logging system.

    This function should be called once during SDK startup.
    """

    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """
    Return a configured logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    structlog.stdlib.BoundLogger
        Configured logger instance.
    """
    return structlog.get_logger(name)
