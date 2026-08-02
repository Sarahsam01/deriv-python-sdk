from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import time


@dataclass(frozen=True, slots=True)
class MetricsSnapshot:
    """Immutable request metrics snapshot."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    retried_requests: int
    timed_out_requests: int
    average_latency: float
    last_successful_request_time: float | None
    last_error_time: float | None
    last_error_type: str | None


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    """Immutable SDK health snapshot safe for logging and diagnostics."""

    connected: bool
    authorized: bool
    started: bool
    pending_requests: int
    active_subscriptions: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    retried_requests: int
    timed_out_requests: int
    average_latency: float
    circuit_breaker_states: dict[str, str] = field(default_factory=dict)
    last_successful_request_time: float | None = None
    last_error_time: float | None = None
    last_error_type: str | None = None


class RequestMetrics:
    """Concurrency-safe request metrics collector."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retried_requests = 0
        self.timed_out_requests = 0
        self._total_latency = 0.0
        self.last_successful_request_time: float | None = None
        self.last_error_time: float | None = None
        self.last_error_type: str | None = None
        self.reset()

    def record_success(self, *, latency: float, retries: int) -> None:
        """
        Record a successful request.

        Parameters
        ----------
        latency:
            Request duration in seconds.
        retries:
            Number of retry attempts used before success.
        """
        with self._lock:
            self.total_requests += 1
            self.successful_requests += 1
            self.retried_requests += retries
            self._total_latency += latency
            self.last_successful_request_time = time()

    def record_failure(
        self,
        *,
        latency: float,
        retries: int,
        exception: Exception,
        timed_out: bool = False,
    ) -> None:
        """
        Record a failed request.

        Parameters
        ----------
        latency:
            Request duration in seconds.
        retries:
            Number of retry attempts used before failure.
        exception:
            Sanitized exception source used for the error type.
        timed_out:
            Whether the failure was a timeout.
        """
        with self._lock:
            self.total_requests += 1
            self.failed_requests += 1
            self.retried_requests += retries
            self.timed_out_requests += int(timed_out)
            self._total_latency += latency
            self.last_error_time = time()
            self.last_error_type = type(exception).__name__

    def snapshot(self) -> MetricsSnapshot:
        """Return a point-in-time immutable metrics snapshot."""
        with self._lock:
            average = (
                self._total_latency / self.total_requests
                if self.total_requests
                else 0.0
            )
            return MetricsSnapshot(
                total_requests=self.total_requests,
                successful_requests=self.successful_requests,
                failed_requests=self.failed_requests,
                retried_requests=self.retried_requests,
                timed_out_requests=self.timed_out_requests,
                average_latency=average,
                last_successful_request_time=self.last_successful_request_time,
                last_error_time=self.last_error_time,
                last_error_type=self.last_error_type,
            )

    def reset(self) -> None:
        """Reset all metrics counters and last-event timestamps."""
        with self._lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.retried_requests = 0
            self.timed_out_requests = 0
            self._total_latency = 0.0
            self.last_successful_request_time = None
            self.last_error_time = None
            self.last_error_type = None
