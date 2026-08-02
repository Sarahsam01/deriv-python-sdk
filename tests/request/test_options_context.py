import pytest

from deriv_sdk.exceptions import TimeoutError
from deriv_sdk.request.context import RequestContext
from deriv_sdk.request.options import RequestOptions
from deriv_sdk.request.retry_policy import RetryPolicy


def test_request_options_from_kwargs_preserves_input_and_splits_metadata():
    policy = RetryPolicy(max_attempts=2)
    kwargs = {
        "timeout": 3.5,
        "expected_msg_type": "ping",
        "retry_policy": policy,
        "custom": "value",
    }

    options, metadata = RequestOptions.from_kwargs(kwargs)

    assert kwargs["timeout"] == 3.5
    assert options.timeout == 3.5
    assert options.expected_msg_type == "ping"
    assert options.retry_policy is policy
    assert metadata == {"custom": "value"}


def test_request_context_retry_state_uses_retries_after_first_attempt():
    policy = RetryPolicy(max_attempts=1, retry_on=(RuntimeError,))
    context = RequestContext(
        payload={"ping": 1},
        options=RequestOptions(retry_policy=policy, request_id="sdk-id"),
    )

    assert context.attempts == 1
    assert context.request_id == "sdk-id"
    assert context.can_retry

    exc = RuntimeError("temporary")
    context.mark_for_retry(exc)

    assert context.retries == 1
    assert context.attempts == 2
    assert context.last_exception is exc
    assert not context.can_retry

    context.response = {"msg_type": "ping"}
    context.clear_retry()

    assert context.exception is None
    assert not context.should_retry
    assert context.response == {"msg_type": "ping"}

    context.reset()

    assert context.response is None
    assert context.retries == 1


def test_retry_policy_delay_and_eligibility():
    policy = RetryPolicy(
        max_attempts=2,
        delay=0.5,
        backoff=3.0,
        max_delay=1.0,
        retry_on=(TimeoutError,),
    )

    assert policy.should_retry(0, TimeoutError("timeout"))
    assert not policy.should_retry(2, TimeoutError("timeout"))
    assert not policy.should_retry(0, RuntimeError())
    assert policy.next_delay(0) == 0.5
    assert policy.next_delay(1) == 1.0


def test_retry_policy_jitter_and_endpoint_override_are_deterministic():
    override = RetryPolicy(
        max_attempts=1,
        initial_delay=1.0,
        jitter=True,
        jitter_source=lambda: 0.5,
    )
    policy = RetryPolicy(endpoint_overrides={"ping": override})

    selected = policy.for_endpoint("ping")

    assert selected is override
    assert selected.next_delay(0) == 0.5


@pytest.mark.parametrize("enabled", [False, True])
def test_retry_policy_enabled_flag(enabled):
    policy = RetryPolicy(max_attempts=1, enabled=enabled, retry_on=(TimeoutError,))

    assert policy.should_retry(0, TimeoutError("timeout")) is enabled
