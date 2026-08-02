"""
===========================================================
Deriv Python SDK

Middleware Base Class

Responsibilities
----------------
• Define middleware interface
• Process requests
• Process responses
• Process exceptions

Version : 2.0
===========================================================
"""

from __future__ import annotations

from deriv_sdk.request.context import RequestContext


class Middleware:
    """
    Base class for SDK middleware.

    Middleware participates in the lifecycle of a single
    request by receiving a shared RequestContext instance.

    Execution order
    ---------------

    before_request()
        ↓
    Transport
        ↓
    after_response()

    If an exception occurs:

    before_request()
        ↓
    Transport
        ↓
    on_exception()
    """

    async def before_request(
        self,
        context: RequestContext,
    ) -> None:
        """
        Executed before the request is sent.

        Middleware may inspect or modify:

        • context.payload
        • context.metadata
        • context.request_id
        • context.retries
        """
        return None

    async def after_response(
        self,
        context: RequestContext,
    ) -> None:
        """
        Executed after a successful response.

        Middleware may inspect or modify:

        • context.response
        • context.metadata
        """
        return None

    async def on_exception(
        self,
        context: RequestContext,
    ) -> None:
        """
        Executed when request execution raises
        an exception.

        Middleware may inspect:

        • context.exception
        • context.metadata
        """
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
