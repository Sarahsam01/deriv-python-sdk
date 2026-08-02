"""
===========================================================
Deriv Python SDK

Middleware Pipeline

Responsibilities
----------------
• Register middleware
• Remove middleware
• Execute request middleware
• Execute response middleware
• Execute exception middleware
• Maintain middleware execution order

Version : 2.0
===========================================================
"""

from __future__ import annotations

from collections.abc import Iterator

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.request.context import RequestContext


class MiddlewarePipeline:
    """
    Executes middleware in a predictable order.

    Request lifecycle:

        before_request()
              │
              ▼
         Transport Layer
              │
              ▼
        after_response()

    Exception lifecycle:

        before_request()
              │
              ▼
         Transport Layer
              │
              ▼
         on_exception()
    """

    def __init__(self) -> None:
        self._middleware: list[Middleware] = []

    # =====================================================
    # Registration
    # =====================================================

    def add(
        self,
        middleware: Middleware,
    ) -> None:
        """
        Register middleware.
        """
        self._middleware.append(middleware)

    def remove(
        self,
        middleware: Middleware,
    ) -> None:
        """
        Remove middleware.

        If the middleware is not registered,
        the operation is ignored.
        """
        try:
            self._middleware.remove(middleware)
        except ValueError:
            pass

    def clear(self) -> None:
        """
        Remove all middleware.
        """
        self._middleware.clear()

    @property
    def middleware(self) -> tuple[Middleware, ...]:
        """
        Registered middleware.
        """
        return tuple(self._middleware)

    # =====================================================
    # Request Pipeline
    # =====================================================

    async def before_request(
        self,
        context: RequestContext,
    ) -> None:
        """
        Execute request middleware in registration order.
        """
        for middleware in self._middleware:
            await middleware.before_request(context)

    # =====================================================
    # Response Pipeline
    # =====================================================

    async def after_response(
        self,
        context: RequestContext,
    ) -> None:
        """
        Execute response middleware in reverse order.
        """
        for middleware in reversed(self._middleware):
            await middleware.after_response(context)

    # =====================================================
    # Exception Pipeline
    # =====================================================

    async def on_exception(
        self,
        context: RequestContext,
    ) -> None:
        """
        Execute exception middleware in reverse order.
        """
        for middleware in reversed(self._middleware):
            await middleware.on_exception(context)

    # =====================================================
    # Utilities
    # =====================================================

    def __len__(self) -> int:
        return len(self._middleware)

    def __iter__(self) -> Iterator[Middleware]:
        return iter(self._middleware)

    def __contains__(
        self,
        middleware: Middleware,
    ) -> bool:
        return middleware in self._middleware

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(middleware={len(self)})"
