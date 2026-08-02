import asyncio

import pytest

from deriv_sdk.exceptions import TimeoutError as DerivTimeoutError
from deriv_sdk.request.engine import RequestEngine
from deriv_sdk.request.id_generator import UUIDRequestIdGenerator
from deriv_sdk.request.registry import RequestRegistry
from deriv_sdk.request.retry_policy import RetryPolicy


class FakeTransport:
    def __init__(self, outcomes: list[dict[str, object] | Exception]) -> None:
        self.outcomes = outcomes
        self.calls: list[tuple[dict[str, object], str, float]] = []
        self.connected = True

    async def request(
        self,
        message: dict[str, object],
        *,
        expected: str,
        timeout: float = 10.0,
    ) -> dict[str, object]:
        self.calls.append((message, expected, timeout))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.mark.asyncio
async def test_request_registry_lifecycle():
    registry = RequestRegistry()
    future = registry.register(1)

    assert 1 in registry
    assert registry.get(1) is future
    assert registry.resolve(1, {"msg_type": "ping"})
    assert await future == {"msg_type": "ping"}
    assert registry.pending == 0

    failed = registry.register("sdk-id")
    assert registry.reject("sdk-id", RuntimeError("failed"))
    with pytest.raises(RuntimeError):
        await failed

    registry.register(2)
    registry.unregister(2)
    assert len(registry) == 0

    registry.register(3)
    registry.clear()
    assert len(registry) == 0


def test_request_id_generator_returns_unique_strings():
    generator = UUIDRequestIdGenerator()

    first = generator.generate()
    second = generator()

    assert isinstance(first, str)
    assert isinstance(second, str)
    assert first != second


@pytest.mark.asyncio
async def test_request_engine_success_and_metadata_preserved():
    transport = FakeTransport([{"msg_type": "ping", "ping": "pong"}])
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    response = await engine.send(
        {"ping": 1},
        timeout=2.0,
        custom_metadata="kept",
    )

    assert response == {"msg_type": "ping", "ping": "pong"}
    assert transport.calls == [({"ping": 1}, "ping", 2.0)]


@pytest.mark.asyncio
async def test_request_engine_retry_success():
    transport = FakeTransport(
        [
            DerivTimeoutError("timeout"),
            {"msg_type": "ping", "ping": "pong"},
        ]
    )
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    response = await engine.send(
        {"ping": 1},
        retry_policy=RetryPolicy(max_attempts=1, retry_on=(DerivTimeoutError,)),
    )

    assert response["msg_type"] == "ping"
    assert len(transport.calls) == 2


@pytest.mark.asyncio
async def test_request_engine_retry_exhausted():
    transport = FakeTransport(
        [
            DerivTimeoutError("one"),
            DerivTimeoutError("two"),
        ]
    )
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    with pytest.raises(DerivTimeoutError, match="two"):
        await engine.send(
            {"ping": 1},
            retry_policy=RetryPolicy(max_attempts=1, retry_on=(DerivTimeoutError,)),
        )

    assert len(transport.calls) == 2


@pytest.mark.asyncio
async def test_request_engine_non_retryable_exception():
    transport = FakeTransport([ValueError("bad")])
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="bad"):
        await engine.send(
            {"ping": 1},
            retry_policy=RetryPolicy(max_attempts=1, retry_on=(TimeoutError,)),
        )

    assert len(transport.calls) == 1


@pytest.mark.asyncio
async def test_request_engine_requires_expected_for_empty_payload():
    transport = FakeTransport([])
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Unable to determine"):
        await engine.send({})


@pytest.mark.asyncio
async def test_request_engine_api_error_propagates():
    transport = FakeTransport([RuntimeError("APIError: bad request")])
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="APIError"):
        await engine.send({"ping": 1})


@pytest.mark.asyncio
async def test_request_engine_timeout_propagates_without_retry():
    transport = FakeTransport([DerivTimeoutError("timeout")])
    engine = RequestEngine(transport)  # type: ignore[arg-type]

    with pytest.raises(DerivTimeoutError, match="timeout"):
        await engine.send({"ping": 1})

    await asyncio.sleep(0)
