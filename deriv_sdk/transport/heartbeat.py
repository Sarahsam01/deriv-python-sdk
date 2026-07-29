"""
===========================================================
Deriv SDK

Heartbeat Service

Maintains the WebSocket connection by periodically
sending ping requests.

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from deriv_sdk.logger import get_logger
from deriv_sdk.transport.messages import PingRequest


class Heartbeat:
    """
    Periodically sends PingRequest messages.
    """

    def __init__(
        self,
        sender: Callable[[dict], Awaitable[None]],
        interval: int = 20,
    ) -> None:
        self._logger = get_logger(__name__)
        self._sender = sender
        self._interval = interval
        self._task: asyncio.Task | None = None
        self._running = False

    @property
    def running(self) -> bool:
        """Return True if the heartbeat is active."""
        return self._running

    async def start(self) -> None:
        """Start the heartbeat loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

        self._logger.info("Heartbeat started.")

    async def stop(self) -> None:
        """Stop the heartbeat loop."""
        self._running = False

        if self._task is not None:
            self._task.cancel()

            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self._logger.info("Heartbeat stopped.")

    async def _run(self) -> None:
        """Heartbeat loop."""
        while self._running:
            await asyncio.sleep(self._interval)

            self._logger.info("Sending heartbeat.")

            await self._sender(PingRequest().to_dict())
