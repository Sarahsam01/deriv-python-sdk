from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from time import monotonic

from deriv_sdk.exceptions import CircuitOpenError


class CircuitBreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


FailurePredicate = Callable[[Exception], bool]
TimeSource = Callable[[], float]


def _default_failure_predicate(exception: Exception) -> bool:
    return not isinstance(exception, asyncio.CancelledError)


@dataclass(slots=True)
class CircuitBreakerSnapshot:
    name: str
    state: CircuitBreakerState
    failures: int
    half_open_successes: int
    half_open_in_flight: int


class CircuitBreaker:
    def __init__(
        self,
        *,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_probe_limit: int = 1,
        success_threshold: int = 1,
        failure_predicate: FailurePredicate | None = None,
        time_source: TimeSource = monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1.")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative.")
        if half_open_probe_limit < 1:
            raise ValueError("half_open_probe_limit must be at least 1.")
        if success_threshold < 1:
            raise ValueError("success_threshold must be at least 1.")

        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_probe_limit = half_open_probe_limit
        self.success_threshold = success_threshold
        self.failure_predicate = failure_predicate or _default_failure_predicate
        self._time_source = time_source
        self._state = CircuitBreakerState.CLOSED
        self._failures = 0
        self._opened_at: float | None = None
        self._half_open_successes = 0
        self._half_open_in_flight = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitBreakerState:
        if self._state is CircuitBreakerState.OPEN and self._opened_at is not None:
            if self._time_source() - self._opened_at >= self.recovery_timeout:
                self._state = CircuitBreakerState.HALF_OPEN
        return self._state

    async def before_request(self) -> None:
        async with self._lock:
            state = self.state
            if state is CircuitBreakerState.OPEN:
                raise CircuitOpenError(
                    "Circuit breaker is open.",
                    code="CircuitOpen",
                    details={"circuit": self.name},
                )

            if state is CircuitBreakerState.HALF_OPEN:
                if self._half_open_in_flight >= self.half_open_probe_limit:
                    raise CircuitOpenError(
                        "Circuit breaker is half-open and probe limit is reached.",
                        code="CircuitHalfOpen",
                        details={"circuit": self.name},
                    )
                self._half_open_in_flight += 1

    async def after_success(self) -> None:
        async with self._lock:
            if self._state is CircuitBreakerState.HALF_OPEN:
                self._half_open_in_flight = max(0, self._half_open_in_flight - 1)
                self._half_open_successes += 1
                if self._half_open_successes >= self.success_threshold:
                    self._close()
                return
            self._failures = 0

    async def after_failure(self, exception: Exception) -> None:
        async with self._lock:
            if self._state is CircuitBreakerState.HALF_OPEN:
                self._half_open_in_flight = max(0, self._half_open_in_flight - 1)

            if not self.failure_predicate(exception):
                return

            self._failures += 1
            self._half_open_successes = 0
            if (
                self._state is CircuitBreakerState.HALF_OPEN
                or self._failures >= self.failure_threshold
            ):
                self._open()

    def snapshot(self) -> CircuitBreakerSnapshot:
        return CircuitBreakerSnapshot(
            name=self.name,
            state=self.state,
            failures=self._failures,
            half_open_successes=self._half_open_successes,
            half_open_in_flight=self._half_open_in_flight,
        )

    def _open(self) -> None:
        self._state = CircuitBreakerState.OPEN
        self._opened_at = self._time_source()
        self._half_open_in_flight = 0

    def _close(self) -> None:
        self._state = CircuitBreakerState.CLOSED
        self._failures = 0
        self._opened_at = None
        self._half_open_successes = 0
        self._half_open_in_flight = 0
