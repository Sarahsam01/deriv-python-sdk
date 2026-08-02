"""
===========================================================
Deriv Python SDK

Request Options

Responsibilities
----------------
• Strongly typed request configuration
• Shared execution settings
• Retry policy configuration
• Construct options from keyword arguments

Version : 3.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

from deriv_sdk.request.retry_policy import RetryPolicy
from deriv_sdk.resilience.circuit_breaker import CircuitBreaker
from deriv_sdk.resilience.rate_limiter import AsyncRateLimiter


@dataclass(slots=True)
class RequestOptions:
    """
    Strongly typed execution options for a single request.

    RequestOptions contains SDK-defined execution settings.
    Any remaining keyword arguments are treated as user
    metadata and stored separately in RequestContext.
    """

    # =====================================================
    # Transport
    # =====================================================

    timeout: float | None = None

    # =====================================================
    # Response Validation
    # =====================================================

    expected_msg_type: str | None = None

    # =====================================================
    # Diagnostics
    # =====================================================

    endpoint: str | None = None

    service_name: str | None = None

    request_id: str | None = None

    # =====================================================
    # Retry
    # =====================================================

    retry_policy: RetryPolicy = field(
        default_factory=RetryPolicy,
    )

    # =====================================================
    # Resilience
    # =====================================================

    circuit_breaker: CircuitBreaker | None = None
    rate_limiter: AsyncRateLimiter | None = None

    # =====================================================
    # Factory
    # =====================================================

    @classmethod
    def from_kwargs(
        cls,
        kwargs: dict[str, Any],
    ) -> tuple[RequestOptions, dict[str, Any]]:
        """
        Build RequestOptions from keyword arguments.

        Returns
        -------
        tuple
            (
                RequestOptions,
                remaining_metadata,
            )
        """

        kwargs = dict(kwargs)

        option_names = {field.name for field in fields(cls)}

        option_values: dict[str, Any] = {}
        metadata: dict[str, Any] = {}

        for key, value in kwargs.items():
            if key in option_names:
                option_values[key] = value
            else:
                metadata[key] = value

        return (
            cls(**option_values),
            metadata,
        )

    # =====================================================
    # Helpers
    # =====================================================

    def copy(self) -> RequestOptions:
        """
        Return a shallow copy of this instance.
        """

        return type(self)(
            timeout=self.timeout,
            expected_msg_type=self.expected_msg_type,
            endpoint=self.endpoint,
            service_name=self.service_name,
            request_id=self.request_id,
            retry_policy=self.retry_policy,
            circuit_breaker=self.circuit_breaker,
            rate_limiter=self.rate_limiter,
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"endpoint={self.endpoint!r}, "
            f"service_name={self.service_name!r}, "
            f"timeout={self.timeout!r}, "
            f"expected_msg_type={self.expected_msg_type!r}, "
            f"request_id={self.request_id!r}"
            f")"
        )
