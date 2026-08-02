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
from collections.abc import Awaitable, Callable
from typing import Any

from deriv_sdk.exceptions import TimeoutError
from deriv_sdk.middleware.base import Middleware
from deriv_sdk.middleware.logging import LoggingMiddleware
from deriv_sdk.middleware.pipeline import MiddlewarePipeline
from deriv_sdk.middleware.retry import RetryMiddleware
from deriv_sdk.middleware.validation import ValidationMiddleware
from deriv_sdk.request.context import RequestContext
from deriv_sdk.request.id_generator import RequestIdGenerator, UUIDRequestIdGenerator
from deriv_sdk.request.metrics import HealthSnapshot, RequestMetrics
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
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:

        self._transport = transport
        self._request_id_generator = request_id_generator or UUIDRequestIdGenerator()
        self._pipeline = MiddlewarePipeline()
        self._sleep = sleep
        self._metrics = RequestMetrics()

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

    @property
    def metrics(self) -> RequestMetrics:
        return self._metrics

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
        breaker = context.options.circuit_breaker
        limiter = context.options.rate_limiter

        while True:
            context.reset()

            await self._pipeline.before_request(
                context,
            )

            try:
                if breaker is not None:
                    await breaker.before_request()

                if limiter is not None:
                    await limiter.acquire()

                expected = context.options.expected_msg_type
                if expected is None:
                    raise ValueError("Expected response type is required.")

                timeout = context.options.timeout

                context.response = await self._transport.request(
                    context.payload,
                    expected=expected,
                    timeout=timeout if timeout is not None else 10.0,
                )

                await self._pipeline.after_response(
                    context,
                )

                if breaker is not None:
                    await breaker.after_success()

                self._metrics.record_success(
                    latency=context.elapsed,
                    retries=context.retries,
                )

                return context.response

            except Exception as exc:
                context.exception = exc

                if breaker is not None:
                    await breaker.after_failure(exc)

                await self._pipeline.on_exception(
                    context,
                )

                if not context.should_retry:
                    self._metrics.record_failure(
                        latency=context.elapsed,
                        retries=context.retries,
                        exception=exc,
                        timed_out=isinstance(exc, TimeoutError),
                    )
                    raise

                policy = context.options.retry_policy.for_endpoint(
                    context.options.endpoint
                )
                delay = policy.next_delay(
                    context.retries - 1,
                )

                if delay > 0:
                    await self._sleep(delay)

    def health_snapshot(
        self,
        *,
        started: bool = False,
        authorized: bool = False,
        active_subscriptions: int = 0,
    ) -> HealthSnapshot:
        """
        Return a typed health snapshot for diagnostics.

        Parameters
        ----------
        started:
            Whether the owning client has completed startup.
        authorized:
            Whether the owning client is authorized.
        active_subscriptions:
            Number of active streaming subscriptions.

        Returns
        -------
        HealthSnapshot
            Log-safe runtime health and metrics summary.
        """
        metrics = self._metrics.snapshot()
        pending = getattr(self._transport, "pending_requests", 0)
        return HealthSnapshot(
            connected=self.connected,
            authorized=authorized,
            started=started,
            pending_requests=pending,
            active_subscriptions=active_subscriptions,
            total_requests=metrics.total_requests,
            successful_requests=metrics.successful_requests,
            failed_requests=metrics.failed_requests,
            retried_requests=metrics.retried_requests,
            timed_out_requests=metrics.timed_out_requests,
            average_latency=metrics.average_latency,
            last_successful_request_time=metrics.last_successful_request_time,
            last_error_time=metrics.last_error_time,
            last_error_type=metrics.last_error_type,
        )

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
