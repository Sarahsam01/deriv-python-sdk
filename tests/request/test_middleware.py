import asyncio
import logging

import pytest

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.middleware.logging import LoggingMiddleware
from deriv_sdk.middleware.pipeline import MiddlewarePipeline
from deriv_sdk.middleware.retry import RetryMiddleware
from deriv_sdk.middleware.validation import ValidationMiddleware
from deriv_sdk.request.context import RequestContext
from deriv_sdk.request.options import RequestOptions
from deriv_sdk.request.retry_policy import RetryPolicy


class RecordingMiddleware(Middleware):
    def __init__(self, name: str, events: list[str]) -> None:
        self.name = name
        self.events = events

    async def before_request(self, context: RequestContext) -> None:
        self.events.append(f"before:{self.name}")

    async def after_response(self, context: RequestContext) -> None:
        self.events.append(f"after:{self.name}")

    async def on_exception(self, context: RequestContext) -> None:
        self.events.append(f"exception:{self.name}")


class FailingMiddleware(Middleware):
    async def before_request(self, context: RequestContext) -> None:
        raise RuntimeError("middleware failed")


@pytest.mark.asyncio
async def test_middleware_ordering():
    events: list[str] = []
    pipeline = MiddlewarePipeline()
    pipeline.add(RecordingMiddleware("one", events))
    pipeline.add(RecordingMiddleware("two", events))
    context = RequestContext(payload={"ping": 1})

    await pipeline.before_request(context)
    await pipeline.after_response(context)
    await pipeline.on_exception(context)

    assert events == [
        "before:one",
        "before:two",
        "after:two",
        "after:one",
        "exception:two",
        "exception:one",
    ]


@pytest.mark.asyncio
async def test_middleware_exception_propagates():
    pipeline = MiddlewarePipeline()
    pipeline.add(FailingMiddleware())

    with pytest.raises(RuntimeError, match="middleware failed"):
        await pipeline.before_request(RequestContext(payload={"ping": 1}))


@pytest.mark.asyncio
async def test_validation_middleware_expected_msg_type():
    middleware = ValidationMiddleware()
    context = RequestContext(
        payload={"ping": 1},
        response={"msg_type": "authorize"},
        options=RequestOptions(expected_msg_type="ping"),
    )

    with pytest.raises(ValueError, match="Unexpected response"):
        await middleware.after_response(context)


@pytest.mark.asyncio
async def test_retry_middleware_decides_only():
    middleware = RetryMiddleware()
    context = RequestContext(
        payload={"ping": 1},
        exception=TimeoutError(),
        options=RequestOptions(
            retry_policy=RetryPolicy(max_attempts=1, retry_on=(TimeoutError,))
        ),
    )

    await middleware.on_exception(context)

    assert context.should_retry
    assert context.retries == 1


@pytest.mark.asyncio
async def test_logging_middleware_is_concurrency_safe_and_redacts(caplog):
    middleware = LoggingMiddleware()
    caplog.set_level(logging.DEBUG, logger="deriv_sdk.request")

    contexts = [
        RequestContext(
            payload={"authorize": f"secret-{index}"},
            response={"msg_type": "authorize"},
            options=RequestOptions(endpoint="authorize", request_id=str(index)),
        )
        for index in range(3)
    ]

    await asyncio.gather(*(middleware.before_request(context) for context in contexts))
    await asyncio.gather(*(middleware.after_response(context) for context in contexts))

    payloads = [record.__dict__.get("payload") for record in caplog.records]
    log_text = f"{caplog.text} {payloads}"
    assert "***" in log_text
    assert "secret-0" not in log_text
    assert "secret-1" not in log_text
    assert "secret-2" not in log_text
