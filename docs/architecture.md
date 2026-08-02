# Architecture Guide

Stable release tag: `v1.0.0`

Python package version: `1.0.0`

## Overview

The SDK separates public services from transport details. Application code uses
`DerivClient`; services use `RequestEngine`; only the transport owns the
WebSocket connection.

```text
DerivClient
    |
    v
Service Registry
    |
    v
BaseService / BaseTradingService
    |
    v
RequestEngine
    |
    v
Middleware Pipeline
    |
    v
WebSocketClient
    |
    v
Deriv WebSocket API
```

## Client Composition

`DerivClient` owns:

- `SDKConfig`
- `WebSocketClient`
- `RequestEngine`
- service registry
- auth, market, proposal, buy, balance, contract, and transaction services

Services share one request engine and one transport. This keeps request
correlation, middleware, retries, timeouts, metrics, and cleanup centralized.

## Request Lifecycle

```text
Service method
    |
    v
Build typed request payload
    |
    v
RequestEngine creates RequestContext
    |
    v
Middleware.before_request()
    |
    v
Circuit breaker check
    |
    v
Rate limiter wait
    |
    v
WebSocketClient.request()
    |
    v
RequestRegistry tracks req_id future
    |
    v
Background receiver resolves future
    |
    v
Middleware.after_response()
    |
    v
Typed response model returned
```

If an exception occurs, `Middleware.on_exception()` runs in reverse order.
`RetryMiddleware` only updates retry state. The engine decides whether to
sleep and attempt again.

## Streaming Lifecycle

```text
client.market.subscribe_ticks(symbol)
    |
    v
TickStream sends subscription request
    |
    v
Subscription registered by SubscriptionManager
    |
    v
WebSocketClient.receive() gets messages
    |
    v
MarketService.dispatch_stream()
    |
    v
TickStream.dispatch()
    |
    v
Subscription queue
    |
    v
async for tick in subscription
```

Only `WebSocketClient.receive()` calls `recv()`. Late responses after timeouts
are ignored safely because the request registry unregisters timed-out request
ids.

## Retry Flow

```text
Attempt fails
    |
    v
RequestContext.exception set
    |
    v
RetryMiddleware checks RetryPolicy
    |
    v
RequestEngine sleeps using policy delay
    |
    v
RequestContext reset for next attempt
    |
    v
Transport executes again
```

`RetryPolicy.max_attempts` means retries after the first attempt. API,
validation, client-closed, and circuit-open errors are non-retryable by
default.

## Circuit Breaker

```text
CLOSED
  | failures reach threshold
  v
OPEN
  | recovery timeout elapsed
  v
HALF_OPEN
  | enough probe successes
  v
CLOSED
```

When open, the breaker rejects requests before transport execution. In
half-open state, a limited number of probe requests are allowed.

## Rate Limiter

`AsyncRateLimiter` uses a token bucket:

```text
tokens available -> request proceeds
no tokens        -> task sleeps until next token
```

The limiter uses monotonic time, does not busy loop, and can be scoped per
request or reused as a per-endpoint bucket.

## Concurrent Requests

Concurrent requests are correlated by Deriv `req_id`:

```text
Request A -> req_id 1 -> Future A
Request B -> req_id 2 -> Future B

Receiver gets req_id 2 -> resolves Future B
Receiver gets req_id 1 -> resolves Future A
```

`RequestRegistry` stores pending futures and removes them on success, timeout,
disconnect, or shutdown.

## Cleanup

`DerivClient.close()` delegates to the transport. Transport shutdown:

1. Stops heartbeat.
2. Cancels receiver task.
3. Closes the WebSocket connection.
4. Rejects pending request futures with `ClientClosedError`.
5. Clears the registry.

Repeated close calls are safe.
