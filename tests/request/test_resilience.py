import asyncio

import pytest

from deriv_sdk.exceptions import CircuitOpenError
from deriv_sdk.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerState
from deriv_sdk.resilience.rate_limiter import AsyncRateLimiter


@pytest.mark.asyncio
async def test_circuit_breaker_full_state_transition():
    now = 0.0
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=5.0,
        success_threshold=2,
        time_source=lambda: now,
    )

    await breaker.before_request()
    await breaker.after_failure(RuntimeError("one"))
    assert breaker.state is CircuitBreakerState.CLOSED

    await breaker.before_request()
    await breaker.after_failure(RuntimeError("two"))
    assert breaker.state is CircuitBreakerState.OPEN

    with pytest.raises(CircuitOpenError):
        await breaker.before_request()

    now = 5.0
    assert breaker.state is CircuitBreakerState.HALF_OPEN

    await breaker.before_request()
    await breaker.after_success()
    assert breaker.state is CircuitBreakerState.HALF_OPEN

    await breaker.before_request()
    await breaker.after_success()
    assert breaker.state is CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_rate_limiter_cancellation_safe_wait():
    sleeps: list[float] = []
    now = 0.0

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)
        raise asyncio.CancelledError

    limiter = AsyncRateLimiter(
        rate=1,
        burst=1,
        time_source=lambda: now,
        sleep=fake_sleep,
    )

    await limiter.acquire()

    with pytest.raises(asyncio.CancelledError):
        await limiter.acquire()

    assert sleeps == [1.0]
