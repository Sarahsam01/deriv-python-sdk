import asyncio

import pytest

from deriv_sdk.request.engine import RequestEngine


class ConcurrentTransport:
    connected = True
    pending_requests = 0

    async def request(
        self,
        message: dict[str, object],
        *,
        expected: str,
        timeout: float = 10.0,
    ) -> dict[str, object]:
        await asyncio.sleep(0)
        return {"msg_type": expected, "echo": message}


@pytest.mark.asyncio
async def test_hundreds_of_concurrent_mocked_requests_are_stable():
    engine = RequestEngine(ConcurrentTransport())  # type: ignore[arg-type]

    responses = await asyncio.gather(
        *(engine.send({"ping": index}) for index in range(250))
    )

    assert len(responses) == 250
    assert engine.metrics.snapshot().successful_requests == 250
