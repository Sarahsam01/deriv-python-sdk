"""
===========================================================
Deriv Python SDK

Request Context

Responsibilities
----------------
• Carry request state
• Carry response state
• Carry exception state
• Carry request options
• Carry middleware metadata
• Track request timing
• Manage retry state

Version : 3.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from deriv_sdk.request.options import RequestOptions


@dataclass(slots=True)
class RequestContext:
    """
    Shared context for a single SDK request.

    A RequestContext is created by the RequestEngine and
    passed through every middleware during the request
    lifecycle.

    Middleware may inspect or modify the context as needed.
    """

    # =====================================================
    # Request
    # =====================================================

    payload: dict[str, Any]

    # =====================================================
    # Response
    # =====================================================

    response: dict[str, Any] | None = None

    # =====================================================
    # Exception
    # =====================================================

    exception: Exception | None = None

    # =====================================================
    # Request Options
    # =====================================================

    options: RequestOptions = field(
        default_factory=RequestOptions,
    )

    # =====================================================
    # Execution State
    # =====================================================

    # Number of retry attempts already performed.
    retries: int = 0

    # Indicates whether the RequestEngine should retry.
    should_retry: bool = False

    # Last exception encountered during execution.
    last_exception: Exception | None = None

    # Custom middleware/application data.
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # =====================================================
    # Timing
    # =====================================================

    started: float = field(
        default_factory=perf_counter,
    )

    # =====================================================
    # Convenience Properties
    # =====================================================

    @property
    def elapsed(self) -> float:
        """
        Elapsed request execution time in seconds.
        """
        return perf_counter() - self.started

    @property
    def failed(self) -> bool:
        """
        Whether request execution failed.
        """
        return self.exception is not None

    @property
    def succeeded(self) -> bool:
        """
        Whether request execution completed successfully.
        """
        return self.exception is None and self.response is not None

    @property
    def request_id(self) -> str | None:
        """
        Convenience alias for the configured request ID.
        """
        return self.options.request_id

    @request_id.setter
    def request_id(
        self,
        value: str | None,
    ) -> None:
        self.options.request_id = value

    @property
    def attempts(self) -> int:
        """
        Total execution attempts, including the first.
        """
        return self.retries + 1

    @property
    def can_retry(self) -> bool:
        """
        Whether another retry is permitted.
        """
        exception = self.exception or self.last_exception
        policy = self.options.retry_policy.for_endpoint(self.options.endpoint)
        if exception is None:
            return policy.enabled
        return policy.should_retry(self.retries, exception)

    # =====================================================
    # Metadata Helpers
    # =====================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store custom metadata.
        """
        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve custom metadata.
        """
        return self.metadata.get(
            key,
            default,
        )

    # =====================================================
    # Retry Helpers
    # =====================================================

    def mark_for_retry(
        self,
        exception: Exception,
    ) -> None:
        """
        Mark the current request for another attempt.
        """

        self.exception = exception
        self.last_exception = exception
        self.should_retry = True
        self.retries += 1

    def clear_retry(self) -> None:
        """
        Prepare the context for another execution attempt.
        """

        self.exception = None
        self.should_retry = False

    def reset_response(self) -> None:
        """
        Clear the previous response before retrying.
        """
        self.response = None

    def reset(self) -> None:
        """
        Reset transient execution state while preserving
        request configuration and retry count.
        """

        self.response = None
        self.exception = None
        self.should_retry = False

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"request_id={self.request_id!r}, "
            f"endpoint={self.options.endpoint!r}, "
            f"attempts={self.attempts}, "
            f"max_attempts={self.options.retry_policy.max_attempts}, "
            f"succeeded={self.succeeded}"
            f")"
        )
