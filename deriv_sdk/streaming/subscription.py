"""
===========================================================
Deriv SDK

Streaming Subscription

Responsibilities
----------------
• Async subscription object
• Queue incoming streaming messages
• Async iteration support
• Clean unsubscribe

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")


class Subscription(Generic[T]):
    """
    Represents a live streaming subscription.

    Supports:

        async for item in subscription:
            ...
    """

    def __init__(
        self,
        subscription_id: str,
        websocket,
    ) -> None:

        self._subscription_id = subscription_id
        self._websocket = websocket

        self._queue: asyncio.Queue[T] = asyncio.Queue()

        self._closed = False

    @property
    def id(self) -> str:
        """
        Subscription identifier assigned by Deriv.
        """
        return self._subscription_id

    @property
    def closed(self) -> bool:
        """
        True if the subscription has been closed.
        """
        return self._closed

    async def put(
        self,
        item: T,
    ) -> None:
        """
        Add a new item to the subscription queue.
        """

        if self._closed:
            return

        await self._queue.put(item)

    async def get(self) -> T:
        """
        Wait for the next streamed item.
        """

        return await self._queue.get()

    async def unsubscribe(self) -> None:
        """
        Cancel this subscription.
        """

        if self._closed:
            return

        self._closed = True

        await self._websocket.request(
            {
                "forget": self._subscription_id,
            },
            expected="forget",
        )

    def __aiter__(self):
        """
        Support:

            async for item in subscription
        """

        return self

    async def __anext__(self) -> T:
        """
        Return the next streamed item.
        """

        if self._closed:
            raise StopAsyncIteration

        return await self.get()

    def __len__(self) -> int:
        """
        Current queue size.
        """

        return self._queue.qsize()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._subscription_id!r}, "
            f"closed={self._closed}, "
            f"queued={self._queue.qsize()}"
            f")"
        )
