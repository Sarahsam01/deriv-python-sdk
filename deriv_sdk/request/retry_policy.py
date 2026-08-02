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

from dataclasses import dataclass, field


@dataclass(slots=True)
class RetryPolicy:
    """
    Defines how a request should be retried.
    """

    # Maximum retry attempts after the initial request.
    max_attempts: int = 0

    # Initial delay before retrying (seconds).
    delay: float = 0.0

    # Exponential backoff multiplier.
    backoff: float = 2.0

    # Maximum delay between retries.
    max_delay: float | None = None

    # Whether retrying is enabled.
    enabled: bool = True

    # Exception types eligible for retry.
    retry_on: tuple[type[Exception], ...] = field(default_factory=lambda: (Exception,))

    def should_retry(
        self,
        attempt: int,
        exception: Exception,
    ) -> bool:
        """
        Determine whether another retry is permitted.
        """

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

        delay = self.delay * (self.backoff**attempt)

        if self.max_delay is not None:
            delay = min(
                delay,
                self.max_delay,
            )

        return delay
