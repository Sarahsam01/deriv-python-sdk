"""
===========================================================
Deriv SDK

Logger

Provides structured logging for the SDK.

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

import logging
import sys
from typing import cast

import structlog
from structlog.stdlib import BoundLogger


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


def get_logger(name: str) -> BoundLogger:
    """
    Return a configured structured logger.

    Parameters
    ----------
    name:
        Logger name.

    Returns
    -------
    BoundLogger
        Configured logger instance.
    """
    return cast(BoundLogger, structlog.get_logger(name))
