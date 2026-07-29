"""
===========================================================
Deriv SDK

Base Trading Service

Shared functionality for all trading services.

Version : 3.1.0
===========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from deriv_sdk.transport.websocket import WebSocketClient

T = TypeVar("T")


class BaseTradingService(ABC, Generic[T]):
    """
    Generic base class for trading services.

    T represents the model returned by the service.
    """

    def __init__(
        self,
        websocket: WebSocketClient,
    ) -> None:
        self._websocket = websocket

    async def _execute(
        self,
        *,
        payload: Mapping[str, object],
        expected: str | None = None,
    ) -> T:
        """
        Execute a request and return a typed model.

        Parameters
        ----------
        payload
            Request payload to send to the Deriv API.

        expected
            Expected API ``msg_type`` returned by the server.

        Returns
        -------
        T
            Parsed response model.
        """

        if expected is None:
            raise ValueError("'expected' must be provided.")

        response = await self._websocket.request(
            message=dict(payload),
            expected=expected,
        )

        return self._parse_response(response)

    @abstractmethod
    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> T:
        """
        Convert the API response into a strongly typed model.
        """
        raise NotImplementedError
