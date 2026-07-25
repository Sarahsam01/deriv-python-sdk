"""
===========================================================
Deriv SDK

Client

Main SDK entry point.

Version : 0.2.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .config import SDKConfig
from .version import __version__

if TYPE_CHECKING:
    from .auth.service import AuthService
    from .transport.websocket import WebSocketClient


@dataclass(slots=True)
class DerivClient:
    """
    Main SDK client.
    """

    config: SDKConfig = field(default_factory=SDKConfig)

    websocket: "WebSocketClient" = field(init=False)
    auth: "AuthService" = field(init=False)

    def __post_init__(self) -> None:
        # Import here to avoid circular imports
        from .auth.service import AuthService
        from .transport.websocket import WebSocketClient

        self.websocket = WebSocketClient(self.config)
        self.auth = AuthService(self.websocket, self.config)

    @property
    def version(self) -> str:
        return __version__

    @property
    def connected(self) -> bool:
        return self.websocket.connected

    @property
    def authorized(self) -> bool:
        return self.auth.authorized

    async def connect(self) -> None:
        """Connect to Deriv."""
        await self.websocket.connect()

    async def disconnect(self) -> None:
        """Disconnect from Deriv."""
        await self.websocket.disconnect()

    async def authorize(self):
        """Authorize using the configured API token."""
        return await self.auth.authorize()

    def __repr__(self) -> str:
        return (
            "DerivClient("
            f"version='{self.version}', "
            f"connected={self.connected}, "
            f"authorized={self.authorized})"
        )