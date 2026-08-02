"""
Deriv SDK
"""

from .client import DerivClient
from .config import SDKConfig
from .version import __version__

__all__ = [
    "DerivClient",
    "SDKConfig",
    "__version__",
]
