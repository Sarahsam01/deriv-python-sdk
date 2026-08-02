# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows release-candidate versioning until the final
`v1.0.0` release.

## [1.0.0rc1] - 2026-08-02

Git release-candidate tag: `v1.0.0-rc1`

Python package version: `1.0.0rc1`

### Added

- High-level `DerivClient` entry point with async lifecycle management.
- Concurrent WebSocket transport with request ID correlation.
- Background receiver loop for request responses and streaming messages.
- Central `RequestEngine` for service request execution.
- `RequestContext`, `RequestOptions`, and `RequestRegistry` request primitives.
- Middleware pipeline with logging, validation, and retry middleware.
- Configurable `RetryPolicy` with endpoint overrides and jitter support.
- Circuit breaker support for protecting failing request paths.
- Async token-bucket rate limiter.
- Health and metrics snapshots for runtime observability.
- Secure structured logging with recursive sensitive-field redaction.
- Standardized exception hierarchy.
- Streaming support for tick subscriptions.
- CI-oriented lint, type-check, test, and packaging configuration.
- Packaging metadata for wheel and source distributions.
- README, API reference, and architecture documentation.

### Verified

- Test milestone before final release preparation: 116 passed, 5 skipped.

### Known Limitations

- `active_symbols` may return an empty array for some configured app or
  account environments without an API error.
- This release candidate does not claim unsupported endpoints or successful
  live symbol discovery in every live environment.
