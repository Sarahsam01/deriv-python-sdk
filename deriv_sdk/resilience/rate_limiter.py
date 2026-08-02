from __future__ import annotations

import asyncio
from collections.abc import Callable
from time import monotonic


class AsyncRateLimiter:
    def __init__(
        self,
        *,
        rate: float,
        burst: int | None = None,
        time_source: Callable[[], float] = monotonic,
        sleep: Callable[[float], object] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive.")

        self.rate = rate
        self.burst = burst or max(1, int(rate))
        self._tokens = float(self.burst)
        self._updated_at = time_source()
        self._time_source = time_source
        self._sleep = sleep or asyncio.sleep
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            delay = 0.0
            async with self._lock:
                now = self._time_source()
                elapsed = max(0.0, now - self._updated_at)
                self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
                self._updated_at = now

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return

                delay = (1.0 - self._tokens) / self.rate

            await self._sleep(delay)  # type: ignore[misc]

    @property
    def available_tokens(self) -> float:
        return self._tokens
