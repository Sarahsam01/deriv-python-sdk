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
        if isinstance(value, list):
            return [LoggingMiddleware._redact_mapping(item) for item in value]

        if not isinstance(value, dict):
            return value

        sensitive_keys = {
            "api_token",
            "authorize",
            "email",
            "fullname",
            "loginid",
            "name",
            "token",
        }

        redacted: dict[object, object] = {}
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in sensitive_keys:
                redacted[key] = "***"
            elif isinstance(key, str) and "account" in key.lower():
                redacted[key] = "***"
            else:
                redacted[key] = LoggingMiddleware._redact_mapping(item)
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
            "Sending request.",
            extra={
                "endpoint": context.options.endpoint,
                "service_name": context.options.service_name,
                "request_id": context.request_id,
                "payload": self._redact_mapping(context.payload),
                "retry_count": context.retries,
            },
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
            "Received response.",
            extra={
                "endpoint": context.options.endpoint,
                "service_name": context.options.service_name,
                "request_id": context.request_id,
                "duration": context.elapsed,
                "retry_count": context.retries,
                "response": self._redact_mapping(context.response),
            },
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
            "Request failed.",
            exc_info=context.exception,
            extra={
                "endpoint": context.options.endpoint,
                "service_name": context.options.service_name,
                "request_id": context.request_id,
                "duration": context.elapsed,
                "retry_count": context.retries,
                "error_type": type(context.exception).__name__
                if context.exception is not None
                else None,
            },
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(logger={self._logger.name!r})"
