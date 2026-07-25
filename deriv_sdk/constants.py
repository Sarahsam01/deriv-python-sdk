"""
===========================================================
Deriv SDK

SDK Constants

Version : 0.1.0
===========================================================
"""

from .version import __version__

SDK_NAME = "Deriv SDK"
SDK_VERSION = __version__

DEFAULT_TIMEOUT = 30
DEFAULT_RECONNECT_DELAY = 5
DEFAULT_HEARTBEAT_INTERVAL = 20

DEFAULT_ENVIRONMENT = "demo"

DEFAULT_CURRENCY = "USD"
DEFAULT_LANGUAGE = "EN"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
