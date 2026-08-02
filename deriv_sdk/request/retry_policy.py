"""
===========================================================
Deriv Python SDK

Retry Policy

Responsibilities
----------------
• Define retry behavior
• Configure retry attempts
• Configure retry backoff
• Determine retry eligibility

Version : 1.0
===========================================================
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from deriv_sdk.exceptions import (
    APIError,
    CircuitOpenError,
    ClientClosedError,
    ConnectionError,
    TimeoutError,
    TransportError,
    ValidationError,
)


@dataclass(slots=True)
class RetryPolicy:
    """
    Defines how a request should be retried.
    """

    # Maximum retry attempts after the initial request.
    max_attempts: int = 0

    # Initial delay before retrying (seconds).
    initial_delay: float = 0.0

    # Exponential backoff multiplier.
    backoff_multiplier: float = 2.0

    # Maximum delay between retries.
    max_delay: float | None = None

    # Apply jitter to calculated delays.
    jitter: bool = False

    # Whether retrying is enabled.
    enabled: bool = True

    # Exception types eligible for retry.
    retry_on: tuple[type[Exception], ...] = field(
        default_factory=lambda: (TimeoutError, ConnectionError, TransportError)
    )

    # Exception types that must never be retried.
    no_retry_on: tuple[type[BaseException], ...] = field(
        default_factory=lambda: (
            APIError,
            CircuitOpenError,
            ClientClosedError,
            ValidationError,
        )
    )

    # Endpoint-specific policy overrides.
    endpoint_overrides: dict[str, RetryPolicy] = field(default_factory=dict)

    # Backwards-compatible aliases accepted by older callers.
    delay: float | None = None
    backoff: float | None = None

    # Deterministic test hook for jitter.
    jitter_source: Callable[[], float] = random.random

    def __post_init__(self) -> None:
        if self.delay is not None:
            self.initial_delay = self.delay
        if self.backoff is not None:
            self.backoff_multiplier = self.backoff
        if self.max_attempts < 0:
            raise ValueError("max_attempts must be non-negative.")
        if self.initial_delay < 0:
            raise ValueError("initial_delay must be non-negative.")
        if self.backoff_multiplier < 1:
            raise ValueError("backoff_multiplier must be at least 1.")

    def should_retry(
        self,
        attempt: int,
        exception: Exception,
    ) -> bool:
        """
        Determine whether another retry is permitted.
        """

        if isinstance(exception, self.no_retry_on):
            return False

        if not self.enabled:
            return False

        if attempt >= self.max_attempts:
            return False

        return isinstance(
            exception,
            self.retry_on,
        )

    def next_delay(
        self,
        attempt: int,
    ) -> float:
        """
        Calculate the delay before the next retry.
        """

        delay = self.initial_delay * (self.backoff_multiplier**attempt)

        if self.max_delay is not None:
            delay = min(
                delay,
                self.max_delay,
            )

        if self.jitter and delay > 0:
            delay *= self.jitter_source()

        return delay

    def for_endpoint(self, endpoint: str | None) -> RetryPolicy:
        if endpoint is None:
            return self
        return self.endpoint_overrides.get(endpoint, self)
