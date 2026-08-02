"""
===========================================================
Deriv Python SDK

Base Service

Responsibilities
----------------
• Base class for all SDK services
• Provide access to the Request Engine
• Expose shared configuration and logger
• Centralize request/subscription helpers

Version : 2.0
===========================================================
"""

from __future__ import annotations

import logging
from typing import Any, Protocol, cast, runtime_checkable

from deriv_sdk.config import SDKConfig
from deriv_sdk.request.engine import RequestEngine
from deriv_sdk.transport.websocket import WebSocketClient


@runtime_checkable
class RequestEngineProtocol(Protocol):
    async def send(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]: ...

    async def subscribe(
        self, payload: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]: ...


@runtime_checkable
class RequestTransportProtocol(Protocol):
    async def request(
        self,
        payload: dict[str, Any],
        *,
        expected: str,
    ) -> dict[str, Any]: ...


class BaseService:
    """
    Base class for all SDK services.
    """

    def __init__(
        self,
        engine: RequestEngineProtocol | RequestTransportProtocol,
    ) -> None:
        self._engine = engine

    @property
    def engine(self) -> RequestEngineProtocol | RequestTransportProtocol:
        """
        Shared request engine.
        """
        return self._engine

    @property
    def transport(self) -> WebSocketClient | RequestTransportProtocol | Any:
        """
        Shared transport (read-only access).
        """
        if isinstance(self._engine, RequestEngine):
            return self._engine.transport
        return self._engine

    @property
    def config(self) -> SDKConfig | None:
        """
        SDK configuration.
        """
        return getattr(self.transport, "config", None)

    @property
    def logger(self) -> logging.Logger | Any:
        """
        SDK logger.
        """
        return getattr(self.transport, "logger", logging.getLogger(__name__))

    async def request(
        self,
        payload: dict[str, Any],
        *,
        expected: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Send a request through the Request Engine.
        """
        if isinstance(self._engine, RequestEngine):
            return await self._engine.send(
                payload,
                expected_msg_type=expected,
                **kwargs,
            )
        if expected is None:
            raise ValueError("'expected' must be provided.")
        transport = cast(RequestTransportProtocol, self._engine)
        return await transport.request(payload, expected=expected)

    async def subscribe(
        self,
        payload: dict[str, Any],
        *,
        expected: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Send a subscription request through the Request Engine.
        """
        if isinstance(self._engine, RequestEngine):
            return await self._engine.subscribe(
                payload,
                expected_msg_type=expected,
                **kwargs,
            )
        if expected is None:
            raise ValueError("'expected' must be provided.")
        transport = cast(RequestTransportProtocol, self._engine)
        return await transport.request(payload, expected=expected)
