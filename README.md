# Deriv SDK

Modern asynchronous Python SDK for the official Deriv API.

## Features

- Async API
- WebSocket support
- REST support
- Automatic reconnect
- Market discovery
- Tick streaming
- Proposal generation
- Trading
- Contract monitoring

## Status

Version 0.1.0

Foundation in progress.

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
