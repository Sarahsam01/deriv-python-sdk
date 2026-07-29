"""
===========================================================
Deriv SDK

WebSocket Transport

Responsibilities
----------------
• Manage WebSocket connection
• Send JSON requests
• Receive JSON responses
• Correlate request/response pairs
• Manage heartbeat
• Route streaming messages
• Dispatch router events

Version : 5.0.0
===========================================================
"""

from __future__ import annotations

import asyncio
import builtins
import json
from typing import Any, Self

import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed

from deriv_sdk.config import SDKConfig
from deriv_sdk.exceptions import TimeoutError
from deriv_sdk.logger import get_logger
from deriv_sdk.transport.heartbeat import Heartbeat
from deriv_sdk.transport.router import MessageRouter


class WebSocketClient:
    """
    Low-level transport layer for the Deriv WebSocket API.
    """

    def __init__(
        self,
        config: SDKConfig | None = None,
        router: MessageRouter | None = None,
    ) -> None:

        self._logger = get_logger(__name__)

        self._config = config or SDKConfig()
        self._router = router or MessageRouter()

        self._connection: ClientConnection | None = None
        self._receiver_task: asyncio.Task | None = None

        self._heartbeat = Heartbeat(self.send)

        self._connected = False

        self._market = None

        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}

        self._next_req_id = 1

        self._request_lock = asyncio.Lock()

    # =====================================================
    # Properties
    # =====================================================

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def websocket(self) -> ClientConnection | None:
        return self._connection

    @property
    def router(self) -> MessageRouter:
        return self._router
        # =====================================================
    # Registration
    # =====================================================

    def register_market_service(self, market: Any) -> None:
        """
        Register the market service responsible for
        processing streaming subscription messages.
        """
        self._market = market
        self._logger.debug("Market service registered.")

    # =====================================================
    # Internal Helpers
    # =====================================================

    def _allocate_req_id(self) -> int:
        """
        Allocate a unique request ID.
        """
        req_id = self._next_req_id
        self._next_req_id += 1
        return req_id

    def _cancel_pending(self) -> None:
        """
        Cancel all pending request futures.
        """
        for future in self._pending.values():
            if not future.done():
                future.cancel()

        self._pending.clear()

    async def _dispatch_stream(
        self,
        message: dict[str, Any],
    ) -> bool:
        """
        Dispatch a streaming message to the registered
        market service.

        Returns True if the message was handled.
        """
        if self._market is None:
            return False

        if "subscription" not in message:
            return False

        return await self._market.dispatch_stream(message)

    # =====================================================
    # Connection Management
    # =====================================================

    async def connect(self) -> None:
        """
        Establish a WebSocket connection.
        """

        if self._connected:
            self._logger.debug("Already connected.")
            return

        self._logger.info(
            "Connecting to Deriv...",
            url=self._config.websocket_url,
        )

        self._connection = await websockets.connect(
            self._config.websocket_url,
        )

        self._connected = True

        await self._heartbeat.start()

        self._receiver_task = asyncio.create_task(
            self.receive(),
            name="deriv-websocket-receiver",
        )

        self._logger.info("Connected successfully.")

    async def disconnect(self) -> None:
        """
        Close the WebSocket connection.
        """

        if not self._connected:
            return

        self._connected = False

        try:
            await self._heartbeat.stop()
        except Exception:
            self._logger.exception("Failed stopping heartbeat.")

        if self._receiver_task is not None:
            self._receiver_task.cancel()

            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass
            finally:
                self._receiver_task = None

        if self._connection is not None:
            try:
                await self._connection.close()
            finally:
                self._connection = None

        self._cancel_pending()

        self._logger.info("Disconnected.")
            # =====================================================
    # Sending
    # =====================================================

    async def send(
        self,
        message: dict[str, Any],
    ) -> None:
        """
        Send a JSON message over the websocket.
        """

        if self._connection is None:
            raise RuntimeError("WebSocket is not connected.")

        payload = json.dumps(message)

        await self._connection.send(payload)

        self._logger.debug(
            "Message sent.",
            payload=message,
        )

    # =====================================================
    # Request / Response
    # =====================================================

    async def request(
        self,
        message: dict[str, Any],
        expected: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Send a request and wait for the matching response.
        """

        async with self._request_lock:

            req_id = self._allocate_req_id()

            request = dict(message)
            request["req_id"] = req_id

            loop = asyncio.get_running_loop()

            future: asyncio.Future[dict[str, Any]] = (
                loop.create_future()
            )

            self._pending[req_id] = future

            try:
                await self.send(request)

                response = await asyncio.wait_for(
                    future,
                    timeout=timeout,
                )

            except builtins.TimeoutError as exc:

                self._logger.error(
                    "Request timed out.",
                    req_id=req_id,
                    expected=expected,
                )

                raise TimeoutError(
                    f"Timed out waiting for '{expected}'."
                ) from exc

            finally:
                self._pending.pop(req_id, None)

        #
        # Validate response
        #

        msg_type = response.get("msg_type")

        if msg_type != expected:
            raise RuntimeError(
                f"Unexpected response type. "
                f"Expected '{expected}', "
                f"received '{msg_type}'."
            )

        #
        # API error
        #

        if "error" in response:

            error = response["error"]

            raise RuntimeError(
                f"{error.get('code', 'Error')}: "
                f"{error.get('message', 'Unknown error')}"
            )

        self._logger.debug(
            "Request completed.",
            req_id=req_id,
            msg_type=msg_type,
        )

        return response
        # =====================================================
    # Receiver
    # =====================================================

    async def receive(self) -> None:
        """
        Background receive loop.
        """

        if self._connection is None:
            return

        self._logger.info("Receiver started.")

        try:
            while self._connected:

                raw = await self._connection.recv()

                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")

                try:
                    message: dict[str, Any] = json.loads(raw)

                except json.JSONDecodeError:
                    self._logger.exception(
                        "Received invalid JSON."
                    )
                    continue

                self._logger.debug(
                    "Message received.",
                    message=message,
                )

                #
                # Streaming messages
                #

                if "subscription" in message:

                    handled = await self._dispatch_stream(
                        message,
                    )

                    if handled:
                        continue

                #
                # Request / Response
                #

                req_id = message.get("req_id")

                if isinstance(req_id, int):

                    future = self._pending.get(req_id)

                    if future is not None and not future.done():
                        future.set_result(message)

                #
                # Router dispatch
                #

                try:
                    self._router.dispatch(message)

                except Exception:
                    self._logger.exception(
                        "Router dispatch failed."
                    )

        except ConnectionClosed as exc:

            self._logger.warning(
                "Connection closed.",
                code=exc.code,
                reason=exc.reason,
            )

        except asyncio.CancelledError:

            self._logger.info(
                "Receiver cancelled."
            )

            raise

        except Exception:

            self._logger.exception(
                "Unexpected receiver failure."
            )

        finally:

            self._connected = False

            self._cancel_pending()

            self._logger.info(
                "Receiver stopped."
            )
                # =====================================================
    # Utilities
    # =====================================================

    async def close(self) -> None:
        """
        Alias for disconnect().
        """
        await self.disconnect()

    async def ping(self) -> None:
        """
        Send a WebSocket ping frame.
        """

        if self._connection is None:
            raise RuntimeError(
                "WebSocket is not connected."
            )

        await self._connection.ping()

        self._logger.debug("Ping sent.")

    # =====================================================
    # Async Context Manager
    # =====================================================

    async def __aenter__(self) -> Self:
        """
        Connect automatically when entering
        an async context.
        """

        await self.connect()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        """
        Disconnect automatically when leaving
        an async context.
        """

        await self.disconnect()

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"connected={self._connected}, "
            f"pending={len(self._pending)})"
        )