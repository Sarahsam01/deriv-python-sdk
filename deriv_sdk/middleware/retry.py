"""
===========================================================
Deriv Python SDK

Retry Middleware

Responsibilities
----------------
• Evaluate retry policy
• Decide whether a request should be retried
• Update RequestContext retry state

Version : 1.0
===========================================================
"""

from __future__ import annotations

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.request.context import RequestContext


class RetryMiddleware(Middleware):
    """
    Middleware responsible for retry decisions.

    This middleware never executes retries itself.
    It only evaluates the retry policy and updates
    the RequestContext.

    The RequestEngine owns the retry loop.
    """

    # =====================================================
    # Request
    # =====================================================

    async def before_request(
        self,
        context: RequestContext,
    ) -> None:
        """
        Nothing to do before sending the request.
        """
        return None

    # =====================================================
    # Response
    # =====================================================

    async def after_response(
        self,
        context: RequestContext,
    ) -> None:
        """
        Successful responses clear any retry state.
        """

        context.should_retry = False
        context.exception = None

    # =====================================================
    # Exception
    # =====================================================

    async def on_exception(
        self,
        context: RequestContext,
    ) -> None:
        """
        Evaluate whether the failed request should
        be retried.
        """

        exception = context.exception

        if exception is None:
            return

        policy = context.options.retry_policy
        policy = policy.for_endpoint(context.options.endpoint)

        if not policy.should_retry(
            context.retries,
            exception,
        ):
            context.should_retry = False
            return

        context.mark_for_retry(
            exception,
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
