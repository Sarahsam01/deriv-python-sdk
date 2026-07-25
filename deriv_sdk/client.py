"""
===========================================================
Deriv SDK

Client

Main entry point for the SDK.

Version : 0.1.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import SDKConfig
from .version import __version__


@dataclass(slots=True)
class DerivClient:
    """
    Main SDK client.

    Parameters
    ----------
    config : SDKConfig
        SDK configuration.
    """

    config: SDKConfig = field(default_factory=SDKConfig)

    connected: bool = False
    authorized: bool = False

    @property
    def version(self) -> str:
        """Return the SDK version."""
        return __version__

    def __repr__(self) -> str:
        return (
            "DerivClient("
            f"version='{self.version}', "
            f"connected={self.connected}, "
            f"authorized={self.authorized})"
        )
