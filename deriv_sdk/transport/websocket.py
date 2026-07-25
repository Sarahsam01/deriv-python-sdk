"""
===========================================================
Deriv SDK

WebSocket Client

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

import websockets
from websockets.client import WebSocketClientProtocol

from deriv_sdk.config import SDKConfig
from deriv_sdk.logger import get_logger


class WebSocketClient:
    """
    WebSocket transport for the Deriv SDK.
    """

    def __init__(self, config: SDKConfig):
        self._config = config
        self._logger = get_logger(__name__)
        self._websocket: WebSocketClientProtocol | None = None

    @property
    def connected(self) -> bool:
        """
        Return True if connected.
        """
        return self._websocket is not None

    async def connect(self) -> None:
        """
        Open the WebSocket connection.
        """
        if self.connected:
            return

        self._logger.info("Connecting to Deriv...")

        self._websocket = await websockets.connect(self._config.websocket_url)

        self._logger.info("Connected successfully.")

    async def disconnect(self) -> None:
        """
        Close the WebSocket connection.
        """
        if self._websocket is None:
            return

        await self._websocket.close()

        self._websocket = None

        self._logger.info("Disconnected.")
