"""
===========================================================
Deriv SDK

WebSocket Transport

Responsibilities
----------------
• Connect to Deriv
• Disconnect cleanly
• Send JSON messages
• Wait for request/response pairs
• Start Heartbeat
• Start Receiver

Version : 2.1.0
===========================================================
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed

from deriv_sdk.config import SDKConfig
from deriv_sdk.logger import get_logger
from deriv_sdk.transport.heartbeat import Heartbeat
from deriv_sdk.transport.router import MessageRouter


class WebSocketClient:
    """
    Low-level transport layer for communicating with Deriv.

    This class owns:

        • WebSocket connection
        • Heartbeat
        • Background receiver
        • Pending request futures
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

        # request/response support
        self._pending: dict[str, asyncio.Future] = {}

        self._lock = asyncio.Lock()

    # -----------------------------------------------------
    # Properties
    # -----------------------------------------------------

    @property
    def connected(self) -> bool:
        """True when connected."""

        return self._connected

    @property
    def router(self) -> MessageRouter:
        """Return the message router."""

        return self._router

    # -----------------------------------------------------
    # Connection
    # -----------------------------------------------------

    async def connect(self) -> None:
        """
        Connect to Deriv.
        """

        if self._connected:
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
            name="deriv-receiver",
        )

        self._logger.info("Connected successfully.")

    async def disconnect(self) -> None:
        """
        Disconnect from Deriv.
        """

        if not self._connected:
            return

        self._connected = False

        await self._heartbeat.stop()

        if self._receiver_task is not None:

            self._receiver_task.cancel()

            try:
                await self._receiver_task

            except asyncio.CancelledError:
                pass

        if self._connection is not None:

            await self._connection.close()

            self._connection = None

        # cancel pending requests

        for future in self._pending.values():

            if not future.done():
                future.cancel()

        self._pending.clear()

        self._logger.info("Disconnected.")

    # -----------------------------------------------------
    # Sending
    # -----------------------------------------------------

    async def send(
        self,
        message: dict[str, Any],
    ) -> None:
        """
        Send a JSON message.
        """

        if self._connection is None:

            raise RuntimeError(
                "WebSocket is not connected."
            )

        payload = json.dumps(message)

        await self._connection.send(payload)

        self._logger.debug(
            "Message sent.",
            message=message,
        )

    # -----------------------------------------------------
    # Request / Response
    # -----------------------------------------------------

    async def request(
        self,
        message: dict[str, Any],
        expected: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Send a request and wait for the response.
        """

        async with self._lock:

            loop = asyncio.get_running_loop()

            future: asyncio.Future = loop.create_future()

            self._pending[expected] = future

            await self.send(message)

            try:

                response = await asyncio.wait_for(
                    future,
                    timeout,
                )

                return response

            finally:

                self._pending.pop(
                    expected,
                    None,
                )
                  # -----------------------------------------------------
    # Receiver
    # -----------------------------------------------------

    async def receive(self) -> None:
        """
        Background receive loop.

        Receives messages from Deriv, completes pending
        requests, and dispatches every message through the
        MessageRouter.
        """

        if self._connection is None:
            return

        self._logger.info("Receiver started.")

        try:
            while self._connected:

                raw = await self._connection.recv()

                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")

                message: dict[str, Any] = json.loads(raw)

                self._logger.debug(
                    "Message received.",
                    message=message,
                )

                msg_type = message.get("msg_type")

                if msg_type is not None:

                    future = self._pending.get(msg_type)

                    if (
                        future is not None
                        and not future.done()
                    ):
                        future.set_result(message)

                self._router.dispatch(message)

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

        except json.JSONDecodeError as exc:

            self._logger.exception(
                "Invalid JSON received.",
                error=str(exc),
            )

        except Exception as exc:

            self._logger.exception(
                "Unexpected receiver error.",
                error=str(exc),
            )

        finally:

            self._connected = False

            for future in self._pending.values():

                if not future.done():
                    future.cancel()

            self._pending.clear()

            self._logger.info(
                "Receiver stopped."
            )  