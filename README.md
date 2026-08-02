# Deriv Python SDK

Release candidate tag: `v1.0.0-rc1`

Python package version: `1.0.0rc1`

The Deriv Python SDK is an asynchronous Python client for the Deriv WebSocket
API. It provides a high-level `DerivClient`, typed market and trading models,
request middleware, streaming subscriptions, retries, rate limiting, circuit
breakers, health snapshots, metrics, and secure structured logging.

The SDK is designed for market-data tools, dashboards, diagnostics, and
applications that need a stable async interface to Deriv. Live integration
tests and examples are non-trading by default. This repository does not place
live trades during normal tests.

## Supported Python Versions

- Python 3.12
- Python 3.13
- Python 3.14

## Features

- Async WebSocket client
- High-level `DerivClient`
- Auth service
- Market service for active symbols, tick history, trading times, contracts,
  and tick subscriptions
- Trading service wrappers for proposal, buy, balance, contract, and
  transaction APIs
- Typed response models
- Request middleware pipeline
- Configurable retry policy
- Circuit breaker support
- Async token-bucket rate limiter
- Request health and metrics snapshots
- Structured logging with recursive redaction
- Idempotent startup and shutdown

## Installation

Install from PyPI:

```bash
pip install deriv-sdk
```

Install from source:

```bash
git clone https://github.com/your-org/deriv-sdk.git
cd deriv-sdk
python -m venv venv
venv\Scripts\python.exe -m pip install -e ".[dev]"
```

On macOS or Linux, replace `venv\Scripts\python.exe` with
`venv/bin/python`.

## Quick Start

```python
import asyncio

from deriv_sdk import DerivClient


async def main() -> None:
    client = DerivClient(
        app_id="1089",
        api_token="YOUR_TOKEN",
    )

    try:
        await client.start()
        symbols = await client.market.active_symbols()
        print(f"Loaded {len(symbols)} active symbols")
    finally:
        await client.close()


asyncio.run(main())
```

## Authentication

`app_id` identifies your Deriv application. Use Deriv's public app id for
testing, or your own registered app id for production.

`api_token` authorizes account-specific calls. Keep tokens out of source code.
The SDK redacts token-like fields from logs, but your application should still
load tokens from environment variables or a secret manager.

Common environment variables:

```powershell
$env:DERIV_APP_ID="1089"
$env:DERIV_API_TOKEN="YOUR_TOKEN"
```

Virtual accounts are recommended while developing. Use a virtual account token
for account-specific examples and avoid running buy flows unless you explicitly
intend to trade.

Manual authorization:

```python
client = DerivClient(app_id="1089")
await client.start()
authorize_response = await client.auth.authorize("YOUR_TOKEN")
print(authorize_response["msg_type"])
```

## Client Lifecycle

Start and close explicitly:

```python
client = DerivClient(app_id="1089", api_token="YOUR_TOKEN")
await client.start()
await client.close()
```

Use an async context manager for automatic cleanup:

```python
async with DerivClient(app_id="1089", api_token="YOUR_TOKEN") as client:
    symbols = await client.market.active_symbols()
```

`start()` connects the WebSocket transport and authorizes when `api_token` is
configured. `close()` is idempotent and closes the transport, heartbeat,
receiver task, and pending requests.

## Market Service

Active symbols:

```python
symbols = await client.market.active_symbols(brief=False)
```

Tick history:

```python
history = await client.market.ticks_history("R_100", count=100)
```

Candle history:

```python
candles = await client.market.ticks_history(
    "R_100",
    count=60,
    granularity=60,
    style="candles",
)
```

Trading times:

```python
times = await client.market.trading_times()
```

Contracts for a symbol:

```python
contracts = await client.market.contracts_for("R_100", currency="USD")
```

Tick subscription:

```python
subscription = await client.market.subscribe_ticks("R_100")
try:
    tick = await subscription.__anext__()
    print(tick.quote)
finally:
    await subscription.unsubscribe()
```

## Trading Services

The release candidate exposes safe wrappers for proposal, buy, balance,
contract, and transaction requests.

Proposal quote, which does not place a trade:

```python
quote = await client.proposal.request(
    symbol="R_100",
    contract_type="CALL",
    amount=1.0,
    basis="stake",
    currency="USD",
    duration=5,
    duration_unit="t",
)
print(quote.id)
```

Buy is available as `client.buy.buy(...)`, but it places a real contract
purchase when used with an authorized real account. Do not run buy examples
against a real account unless you deliberately intend to trade:

```python
# Trading example only. Do not run against a real account by accident.
# result = await client.buy.buy(proposal_id=quote.id, price=quote.ask_price)
```

Balance:

```python
balance = await client.balance.get()
print(balance.balance, balance.currency)
```

Contract details:

```python
contract = await client.contract.get(contract_id=123456789)
```

Transaction details:

```python
transaction = await client.transaction.get(transaction_id=123456789)
```

Portfolio and profit table services are not exposed as public `v1.0.0-rc1`
service APIs. Use only documented public services unless a future release adds
those endpoints.

## Streaming

`subscribe_ticks()` returns an async subscription. Iterate over it with
`async for`, and unsubscribe when finished:

```python
subscription = await client.market.subscribe_ticks("R_100")

try:
    async for tick in subscription:
        print(tick.symbol, tick.quote)
        break
finally:
    await subscription.unsubscribe()
```

The WebSocket receiver is the only component that calls `recv()`. Streaming
messages are dispatched from the receiver to the market subscription manager.

## Middleware

Requests pass through the middleware pipeline in this order by default:

```text
LoggingMiddleware
ValidationMiddleware
RetryMiddleware
```

Request flow:

```text
before_request: first to last
transport call
after_response: last to first
on_exception: last to first
```

`LoggingMiddleware` records structured request events and redacts sensitive
fields recursively. `ValidationMiddleware` checks response message type.
`RetryMiddleware` decides whether a failed attempt is eligible for another
try; `RequestEngine` performs the retry loop and sleeps.

## Retry

Configure retry behavior with `RetryPolicy`:

```python
from deriv_sdk.request.retry_policy import RetryPolicy

policy = RetryPolicy(
    enabled=True,
    max_attempts=2,
    initial_delay=0.25,
    backoff_multiplier=2.0,
    max_delay=2.0,
    jitter=True,
)

response = await client.request_engine.send(
    {"ping": 1},
    retry_policy=policy,
)
```

`max_attempts` means retries after the initial attempt. API, validation,
client-closed, and circuit-open errors are not retried by default.

## Circuit Breaker

Use `CircuitBreaker` to reject calls after repeated failures:

```python
from deriv_sdk.resilience import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
)

await client.request_engine.send(
    {"ping": 1},
    circuit_breaker=breaker,
)
```

States:

- `CLOSED`: requests are allowed.
- `OPEN`: requests are rejected with `CircuitOpenError`.
- `HALF_OPEN`: limited probe requests are allowed to test recovery.

## Rate Limiting

Use `AsyncRateLimiter` to limit request bursts:

```python
from deriv_sdk.resilience import AsyncRateLimiter

limiter = AsyncRateLimiter(rate=10, burst=20)

await client.request_engine.send(
    {"ping": 1},
    rate_limiter=limiter,
)
```

Create separate limiter instances for per-endpoint buckets.

## Health and Metrics

```python
health = client.health()
metrics = client.metrics()

print(health.connected)
print(health.pending_requests)
print(metrics.total_requests)
print(metrics.average_latency)

client.reset_metrics()
```

Snapshots are typed and do not contain raw payloads or secrets.

## Exceptions

All public SDK exceptions inherit from `DerivError`:

```text
DerivError
├── ConfigurationError
├── TransportError
│   ├── ConnectionError
│   ├── TimeoutError
│   ├── RequestCancelledError
│   ├── ClientClosedError
│   ├── ReconnectError
│   └── MessageRouterError
├── ValidationError
├── APIError
│   ├── AuthenticationError
│   ├── AuthorizationError
│   ├── ProposalError
│   ├── BuyError
│   ├── ContractError
│   ├── BalanceError
│   └── RateLimitError
├── CircuitOpenError
├── RetryExhaustedError
├── SubscriptionError
└── ParsingError
```

## Examples

The `examples/` directory contains:

- [`examples/live_smoke_test.py`](examples/live_smoke_test.py): opt-in live,
  non-trading smoke test for connection, market data, and tick streaming.
- [`examples/active_symbols_diagnostic.py`](examples/active_symbols_diagnostic.py):
  opt-in diagnostic script for comparing active-symbols request variants.

Run the live smoke test:

```powershell
$env:DERIV_APP_ID="1089"
$env:DERIV_API_TOKEN="YOUR_TOKEN"
venv\Scripts\python.exe examples\live_smoke_test.py
```

`DERIV_API_TOKEN` is optional for public market-data checks.

## Testing

Run non-live tests:

```powershell
venv\Scripts\python.exe -m pytest -v
```

Run quality gates:

```powershell
venv\Scripts\python.exe -m compileall deriv_sdk tests examples
venv\Scripts\python.exe -m ruff format --check .
venv\Scripts\python.exe -m ruff check .
venv\Scripts\python.exe -m mypy deriv_sdk
venv\Scripts\python.exe -m pytest -v
venv\Scripts\python.exe -m build
venv\Scripts\python.exe -m twine check dist\*
```

Live integration tests are marked with `integration` and skipped by default:

```powershell
venv\Scripts\python.exe -m pytest -m integration -v
```

## Contributing

1. Create a virtual environment.
2. Install with development dependencies: `pip install -e ".[dev]"`.
3. Keep public APIs stable unless a change is intentional and documented.
4. Add or update tests for behavior changes.
5. Run the full quality gate before opening a pull request.
6. Never commit API tokens, account identifiers, or `.env` files.

## API and Architecture Documentation

- [API Reference](docs/api.md)
- [Architecture Guide](docs/architecture.md)

## License

MIT. See [`LICENSE`](LICENSE).
