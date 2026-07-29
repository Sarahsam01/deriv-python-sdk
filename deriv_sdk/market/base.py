"""
============================================================
Deriv SDK

Market Base Service

Author : OpenAI
Version: 1.0.0
============================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.transport.websocket import WebSocketClient


class MarketBaseService:
    """
    Base class for all market data services.

    Provides access to the shared WebSocket client.
    """

    def __init__(
        self,
        websocket: WebSocketClient,
    ) -> None:
        self._ws = websocket

    @property
    def websocket(self) -> WebSocketClient:
        """
        Shared websocket client.
        """
        return self._ws

    async def _request(
        self,
        payload: dict[str, Any],
        expected: str,
    ) -> dict[str, Any]:
        """
        Execute a request through the shared transport.
        """
        return await self._ws.request(
            message=payload,
            expected=expected,
        )
