# API Reference

Release candidate tag: `v1.0.0-rc1`

Python package version: `1.0.0rc1`

This page lists the public SDK classes and methods intended for application
code. Internal helpers and private members are intentionally omitted.

## `deriv_sdk.DerivClient`

Main SDK entry point.

Constructor:

```text
DerivClient(*, app_id: str, api_token: str | None = None, config: SDKConfig | None = None)
```

Public lifecycle methods:

- `await client.start() -> None`
- `await client.close() -> None`
- `async with DerivClient(...) as client`

Public diagnostics:

- `client.metrics() -> MetricsSnapshot`
- `client.reset_metrics() -> None`
- `client.health() -> HealthSnapshot`

Public properties:

- `client.config -> SDKConfig`
- `client.transport -> WebSocketClient`
- `client.request_engine -> RequestEngine`
- `client.started -> bool`
- `client.connected -> bool`
- `client.authorized -> bool`
- `client.auth -> AuthService`
- `client.market -> MarketService`
- `client.proposal -> ProposalService`
- `client.buy -> BuyService`
- `client.balance -> BalanceService`
- `client.contract -> ContractService`
- `client.transaction -> TransactionService`

## `SDKConfig`

Configuration object for Deriv connection settings.

Public properties:

- `websocket_url -> str`
- `is_demo -> bool`
- `is_live -> bool`

Public methods:

- `validate() -> None`

## `AuthService`

Authentication service.

Public methods:

- `await authorize(token: str) -> dict[str, Any]`

Public properties:

- `authorized -> bool`
- `authorize_response -> dict[str, Any] | None`

## `MarketService`

Market-data service.

Public methods:

- `await active_symbols(*, brief: bool = True, product_type: str | None = "basic", landing_company_short: str | None = None) -> list[ActiveSymbol]`
- `await ticks_history(symbol: str, *, count: int = 100, start: int | None = None, end: int | str = "latest", granularity: int | None = None, style: str = "ticks") -> TickHistory | CandleHistory`
- `await trading_times(date: str | None = None) -> TradingTimesResponse`
- `await contracts_for(symbol: str, *, currency: str | None = None, product_type: str = "basic") -> ContractsFor`
- `await subscribe_ticks(symbol: str) -> Subscription[Tick]`
- `await dispatch_stream(message: dict) -> bool`

Public properties:

- `subscriptions -> SubscriptionManager`
- `tick_stream -> TickStream`

## Trading Services

### `ProposalService`

- `await request(symbol: str, contract_type: str, amount: float, basis: str = "stake", currency: str = "USD", duration: int = 1, duration_unit: str = "t", barrier: str | None = None) -> Proposal`
- `await quote(proposal: ProposalRequest) -> Proposal`

### `BuyService`

- `await buy(*, proposal_id: str, price: float) -> BuyResult`

This places a contract purchase. Use only when you explicitly intend to trade.

### `BalanceService`

- `await get() -> Balance`

### `ContractService`

- `await get(*, contract_id: int) -> Contract`

### `TransactionService`

- `await get(*, transaction_id: int) -> Transaction`

Portfolio and profit table services are not public services in `v1.0.0-rc1`.

## `RequestEngine`

Central execution engine used by services.

Public methods:

- `add_middleware(middleware: Middleware) -> None`
- `remove_middleware(middleware: Middleware) -> None`
- `clear_middleware() -> None`
- `await send(payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]`
- `await subscribe(payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]`
- `health_snapshot(started: bool = False, authorized: bool = False, active_subscriptions: int = 0) -> HealthSnapshot`

Public properties:

- `transport -> WebSocketClient`
- `pipeline -> MiddlewarePipeline`
- `middleware -> tuple[Middleware, ...]`
- `connected -> bool`
- `metrics -> RequestMetrics`

## `RequestContext`

Per-request state passed through middleware.

Public fields and properties:

- `payload`
- `response`
- `exception`
- `options`
- `retries`
- `should_retry`
- `last_exception`
- `metadata`
- `started`
- `elapsed`
- `failed`
- `succeeded`
- `request_id`
- `attempts`
- `can_retry`

Public methods:

- `set(key: str, value: Any) -> None`
- `get(key: str, default: Any = None) -> Any`
- `mark_for_retry(exception: Exception) -> None`
- `clear_retry() -> None`
- `reset_response() -> None`
- `reset() -> None`

## `RequestOptions`

Typed execution options for a request.

Public fields:

- `timeout`
- `expected_msg_type`
- `endpoint`
- `service_name`
- `request_id`
- `retry_policy`
- `circuit_breaker`
- `rate_limiter`

Public methods:

- `RequestOptions.from_kwargs(kwargs: dict[str, Any]) -> tuple[RequestOptions, dict[str, Any]]`
- `copy() -> RequestOptions`

## `RetryPolicy`

Retry configuration.

Public fields:

- `max_attempts`
- `initial_delay`
- `backoff_multiplier`
- `max_delay`
- `jitter`
- `enabled`
- `retry_on`
- `no_retry_on`
- `endpoint_overrides`
- `delay`
- `backoff`
- `jitter_source`

Public methods:

- `should_retry(attempt: int, exception: Exception) -> bool`
- `next_delay(attempt: int) -> float`
- `for_endpoint(endpoint: str | None) -> RetryPolicy`

## Health and Metrics Snapshots

`HealthSnapshot` fields:

- `connected`
- `authorized`
- `started`
- `pending_requests`
- `active_subscriptions`
- `total_requests`
- `successful_requests`
- `failed_requests`
- `retried_requests`
- `timed_out_requests`
- `average_latency`
- `circuit_breaker_states`
- `last_successful_request_time`
- `last_error_time`
- `last_error_type`

`MetricsSnapshot` fields:

- `total_requests`
- `successful_requests`
- `failed_requests`
- `retried_requests`
- `timed_out_requests`
- `average_latency`
- `last_successful_request_time`
- `last_error_time`
- `last_error_type`

## Resilience Helpers

`CircuitBreaker` public methods:

- `await before_request() -> None`
- `await after_success() -> None`
- `await after_failure(exception: Exception) -> None`
- `snapshot() -> CircuitBreakerSnapshot`

`CircuitBreaker` public property:

- `state -> CircuitBreakerState`

`AsyncRateLimiter` public methods and properties:

- `await acquire() -> None`
- `available_tokens -> float`
