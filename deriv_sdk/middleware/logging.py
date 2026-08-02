"""
===========================================================
Deriv Python SDK

Logging Middleware

Responsibilities
----------------
• Log outgoing requests
• Log incoming responses
• Log request duration
• Log request failures

Version : 2.0
===========================================================
"""

from __future__ import annotations

import logging

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.request.context import RequestContext


class LoggingMiddleware(Middleware):
    """
    Middleware responsible for logging request execution.

    Logging uses the RequestContext, making the middleware
    completely stateless and safe for concurrent requests.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(
            "deriv_sdk.request",
        )

    @staticmethod
    def _redact_mapping(value: object) -> object:
        if not isinstance(value, dict):
            return value

        sensitive_keys = {
            "api_token",
            "authorize",
            "token",
        }

        redacted: dict[object, object] = {}
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in sensitive_keys:
                redacted[key] = "***"
            elif isinstance(item, dict):
                redacted[key] = LoggingMiddleware._redact_mapping(item)
            else:
                redacted[key] = item
        return redacted

    # =====================================================
    # Request
    # =====================================================

    async def before_request(
        self,
        context: RequestContext,
    ) -> None:
        """
        Log an outgoing request.
        """

        self._logger.debug(
            "Sending request [endpoint=%s, request_id=%s]: %s",
            context.options.endpoint,
            context.request_id,
            self._redact_mapping(context.payload),
        )

    # =====================================================
    # Response
    # =====================================================

    async def after_response(
        self,
        context: RequestContext,
    ) -> None:
        """
        Log a successful response.
        """

        self._logger.debug(
            "Received response [endpoint=%s, request_id=%s, elapsed=%.3fs]: %s",
            context.options.endpoint,
            context.request_id,
            context.elapsed,
            self._redact_mapping(context.response),
        )

    # =====================================================
    # Exception
    # =====================================================

    async def on_exception(
        self,
        context: RequestContext,
    ) -> None:
        """
        Log a failed request.
        """

        self._logger.exception(
            "Request failed [endpoint=%s, request_id=%s, elapsed=%.3fs]",
            context.options.endpoint,
            context.request_id,
            context.elapsed,
            exc_info=context.exception,
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(logger={self._logger.name!r})"
