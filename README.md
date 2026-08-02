# Deriv SDK

Modern asynchronous Python SDK for the official Deriv API.

## Features

- Async API
- WebSocket support
- Market discovery
- Tick streaming
- Proposal generation
- Trading
- Contract monitoring
- Configurable retries, timeouts, circuit breakers, and rate limiting
- Typed health and metrics snapshots
- Structured logging with recursive secret redaction
- Idempotent lifecycle cleanup

## Status

Version 1.0.0

Production hardening in progress. Live integration remains opt-in and
non-trading by default.

## Production Hardening

Requests flow through `RequestEngine`, which owns execution, timeout
propagation, retry sleeping, rate limiting, circuit breaker checks, metrics,
and middleware execution. `RetryMiddleware` only decides whether the current
exception is eligible for another attempt.

Retry semantics:

- `max_attempts` means retries after the first attempt.
- `initial_delay`, `backoff_multiplier`, `max_delay`, and optional `jitter`
  control retry delays.
- Transient SDK transport failures are retryable by default.
- API, validation, client-closed, and circuit-open errors are not retried by
  default.
- Endpoint-specific overrides can be supplied through `RetryPolicy`.

Example:

```python
from deriv_sdk.request.retry_policy import RetryPolicy

policy = RetryPolicy(
    max_attempts=2,
    initial_delay=0.25,
    backoff_multiplier=2.0,
    max_delay=2.0,
)

response = await client.request_engine.send(
    {"ping": 1},
    timeout=5.0,
    retry_policy=policy,
)
```

Circuit breakers use `CLOSED`, `OPEN`, and `HALF_OPEN` states with monotonic
timing, configurable failure thresholds, recovery timeout, half-open probe
limits, success thresholds, and a custom failure predicate.

Rate limiting uses an async token bucket with request rate, burst capacity,
monotonic timing, and cancellation-safe waiting. A limiter can be passed per
request, which also allows per-endpoint buckets.

Health and metrics:

```python
metrics = client.metrics()
health = client.health()

print(metrics.total_requests)
print(health.pending_requests)
```

Snapshots never include secrets or raw payloads. Metrics can be reset with
`client.reset_metrics()`.

The public exception hierarchy is rooted at `DerivError` and includes
configuration, transport, timeout, cancellation, client-closed, API,
authentication, authorization, validation, rate-limit, circuit-open,
retry-exhausted, subscription, and parsing errors.

Logging is structured through the SDK logging layer and recursively redacts
authorization tokens, API tokens, emails, names, and account identifiers.
Full authorization responses and raw secrets are not logged.

Lifecycle guarantees:

- `close()` and `disconnect()` are idempotent.
- Partial startup rolls back by closing the transport.
- Heartbeat and receiver tasks are cancelled during shutdown.
- Pending callers receive `ClientClosedError`.
- Late responses after timeout are ignored safely.
- Only the background receiver loop calls `recv()`.

CI quality gates run compile, Ruff format check, Ruff lint, MyPy, pytest,
package build, and Twine validation on every push and pull request.

## Live Smoke Test

The live smoke test connects to the Deriv WebSocket API and exercises public
market-data flows only. It does not place trades. Internet access is required.
`DERIV_API_TOKEN` is optional; when omitted, authorization is skipped and public
market-data checks still run.

Windows CMD:

```cmd
set DERIV_APP_ID=your_app_id
set DERIV_API_TOKEN=your_token
venv\Scripts\python.exe examples\live_smoke_test.py
```

PowerShell:

```powershell
$env:DERIV_APP_ID="your_app_id"
$env:DERIV_API_TOKEN="your_token"
venv\Scripts\python.exe examples\live_smoke_test.py
```

Run live integration tests explicitly:

```powershell
venv\Scripts\python.exe -m pytest -m integration -v
```
