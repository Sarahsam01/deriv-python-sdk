"""
===========================================================
Deriv Python SDK

Request Engine

Responsibilities
----------------
• Execute SDK requests
• Execute middleware pipeline
• Coordinate retry execution
• Delegate transport communication
• Centralize request lifecycle

Version : 4.0
===========================================================
"""

from __future__ import annotations

import asyncio
from typing import Any

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.middleware.logging import LoggingMiddleware
from deriv_sdk.middleware.pipeline import MiddlewarePipeline
from deriv_sdk.middleware.retry import RetryMiddleware
from deriv_sdk.middleware.validation import ValidationMiddleware
from deriv_sdk.request.context import RequestContext
from deriv_sdk.request.id_generator import RequestIdGenerator, UUIDRequestIdGenerator
from deriv_sdk.request.options import RequestOptions
from deriv_sdk.transport.websocket import WebSocketClient


class RequestEngine:
    """
    Central request execution engine.

    Every SDK request flows through this engine.

    Service
        │
        ▼
    RequestContext
        │
        ▼
    Middleware Pipeline
        │
        ▼
    Transport
        │
        ▼
    Middleware Pipeline
        │
        ▼
    Response
    """

    def __init__(
        self,
        transport: WebSocketClient,
        request_id_generator: RequestIdGenerator | None = None,
    ) -> None:

        self._transport = transport
        self._request_id_generator = request_id_generator or UUIDRequestIdGenerator()
        self._pipeline = MiddlewarePipeline()

        # --------------------------------------------------
        # Default Middleware
        # --------------------------------------------------

        self._pipeline.add(
            LoggingMiddleware(),
        )

        self._pipeline.add(
            ValidationMiddleware(),
        )

        self._pipeline.add(
            RetryMiddleware(),
        )

    # =====================================================
    # Properties
    # =====================================================

    @property
    def transport(self) -> WebSocketClient:
        return self._transport

    @property
    def pipeline(self) -> MiddlewarePipeline:
        return self._pipeline

    @property
    def middleware(self) -> tuple[Middleware, ...]:
        return self._pipeline.middleware

    @property
    def connected(self) -> bool:
        return self._transport.connected

    # =====================================================
    # Middleware Management
    # =====================================================

    def add_middleware(
        self,
        middleware: Middleware,
    ) -> None:
        self._pipeline.add(middleware)

    def remove_middleware(
        self,
        middleware: Middleware,
    ) -> None:
        self._pipeline.remove(middleware)

    def clear_middleware(self) -> None:
        self._pipeline.clear()

    # =====================================================
    # Context Factory
    # =====================================================

    def _create_context(
        self,
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> RequestContext:
        """
        Build a RequestContext from request arguments.
        """

        options, metadata = RequestOptions.from_kwargs(kwargs)

        if options.request_id is None:
            options.request_id = self._request_id_generator.generate()

        if options.expected_msg_type is None:
            options.expected_msg_type = self._default_expected_msg_type(payload)

        context = RequestContext(
            payload=dict(payload),
            options=options,
            metadata=metadata,
        )

        return context

    @staticmethod
    def _default_expected_msg_type(payload: dict[str, Any]) -> str:
        """
        Derive the Deriv response ``msg_type`` from the endpoint key.

        Services pass explicit expected message types for endpoint-specific
        cases such as ``ticks_history``. This fallback keeps low-level callers
        compatible for simple one-key payloads like ``{"ping": 1}``.
        """

        endpoint_aliases = {
            "forget": "forget",
            "ticks": "tick",
        }

        for key in payload:
            if key in {"req_id", "subscribe"}:
                continue
            return endpoint_aliases.get(key, key)

        raise ValueError("Unable to determine expected response type.")

    # =====================================================
    # Request Execution
    # =====================================================

    async def send(
        self,
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a request.

        Retry execution is coordinated here while retry
        decisions are delegated to RetryMiddleware.
        """

        context = self._create_context(
            payload,
            **kwargs,
        )

        while True:
            context.reset()

            await self._pipeline.before_request(
                context,
            )

            try:
                expected = context.options.expected_msg_type
                if expected is None:
                    raise ValueError("Expected response type is required.")

                timeout = (
                    context.options.timeout
                    if context.options.timeout is not None
                    else 10.0
                )

                context.response = await self._transport.request(
                    context.payload,
                    expected=expected,
                    timeout=timeout,
                )

                await self._pipeline.after_response(
                    context,
                )

                return context.response

            except Exception as exc:
                context.exception = exc

                await self._pipeline.on_exception(
                    context,
                )

                if not context.should_retry:
                    raise

                delay = context.options.retry_policy.next_delay(
                    context.retries - 1,
                )

                if delay > 0:
                    await asyncio.sleep(delay)

    # =====================================================
    # Subscriptions
    # =====================================================

    async def subscribe(
        self,
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a subscription request.

        Subscription lifecycle management may be added
        in a future version.
        """

        return await self.send(
            payload,
            **kwargs,
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"connected={self.connected}, "
            f"middleware={len(self.middleware)}"
            f")"
        )
