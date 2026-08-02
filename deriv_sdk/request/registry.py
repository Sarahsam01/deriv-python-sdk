"""
===========================================================
Deriv Python SDK

Request Registry

Responsibilities
----------------
• Track pending requests
• Match responses to requests
• Complete waiting Futures
• Remove completed requests

Version : 1.0
===========================================================
"""

from __future__ import annotations

import asyncio
from typing import Any

RequestKey = int | str


class RequestRegistry:
    """
    Registry of pending SDK requests.

    Each outgoing request is associated with an
    asyncio.Future. When the corresponding response
    arrives, the Future is completed.
    """

    def __init__(self) -> None:

        self._pending: dict[
            RequestKey,
            asyncio.Future[dict[str, Any]],
        ] = {}

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        request_id: RequestKey,
    ) -> asyncio.Future[dict[str, Any]]:
        """
        Register a pending request.
        """

        loop = asyncio.get_running_loop()

        future: asyncio.Future[dict[str, Any]] = loop.create_future()

        self._pending[request_id] = future

        return future

    # =====================================================
    # Lookup
    # =====================================================

    def get(
        self,
        request_id: RequestKey,
    ) -> asyncio.Future[dict[str, Any]] | None:
        """
        Return the Future for a request.
        """

        return self._pending.get(
            request_id,
        )

    # =====================================================
    # Completion
    # =====================================================

    def resolve(
        self,
        request_id: RequestKey,
        response: dict[str, Any],
    ) -> bool:
        """
        Complete a pending request.
        """

        future = self._pending.pop(
            request_id,
            None,
        )

        if future is None:
            return False

        if not future.done():
            future.set_result(response)

        return True

    def reject(
        self,
        request_id: RequestKey,
        exception: Exception,
    ) -> bool:
        """
        Fail a pending request.
        """

        future = self._pending.pop(
            request_id,
            None,
        )

        if future is None:
            return False

        if not future.done():
            future.set_exception(exception)

        return True

    # =====================================================
    # Cleanup
    # =====================================================

    def unregister(
        self,
        request_id: RequestKey,
    ) -> None:
        """
        Remove a pending request.
        """

        self._pending.pop(
            request_id,
            None,
        )

    def clear(self) -> None:
        """
        Remove every pending request.
        """

        self._pending.clear()

    # =====================================================
    # Introspection
    # =====================================================

    @property
    def pending(self) -> int:
        """
        Number of pending requests.
        """

        return len(self._pending)

    def __contains__(
        self,
        request_id: RequestKey,
    ) -> bool:
        return request_id in self._pending

    def __len__(self) -> int:
        return len(self._pending)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pending={len(self)})"
