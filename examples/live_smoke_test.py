from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()


def _required_app_id() -> str:
    app_id = os.getenv("DERIV_APP_ID", "").strip()
    if not app_id:
        raise RuntimeError("DERIV_APP_ID is required.")
    return app_id


def _optional_api_token() -> str | None:
    token = os.getenv("DERIV_API_TOKEN", "").strip()
    return token or None


def _select_symbol(symbols: list[Any]) -> Any:
    tradable = [
        symbol
        for symbol in symbols
        if symbol.symbol and symbol.is_open and not symbol.is_suspended
    ]
    synthetic = [
        symbol
        for symbol in tradable
        if symbol.market == "synthetic_index"
        or "synthetic" in symbol.market_display_name.lower()
    ]

    candidates = synthetic or tradable or symbols
    if not candidates:
        raise RuntimeError("No suitable symbol found in active_symbols response.")
    return candidates[0]


def _login_id(authorize_response: dict[str, Any] | None) -> str:
    if authorize_response is None:
        return "not authorized"

    authorize = authorize_response.get("authorize")
    if not isinstance(authorize, dict):
        return "available"

    login_id = authorize.get("loginid")
    if login_id is None:
        return "available"
    return str(login_id)


def _history_count(history: Any) -> int:
    return history.count


def _contracts_count(contracts: Any) -> int:
    return contracts.count


def _market_count(trading_times: Any) -> int:
    return len(trading_times.markets)


async def _collect_ticks(client: Any, symbol: str) -> list[Any]:
    subscription = None
    try:
        subscription = await client.market.subscribe_ticks(symbol)
        ticks: list[Any] = []

        while len(ticks) < 3:
            tick = await asyncio.wait_for(subscription.__anext__(), timeout=10)
            ticks.append(tick)

        return ticks
    finally:
        if subscription is not None and not subscription.closed:
            await asyncio.wait_for(subscription.unsubscribe(), timeout=10)


async def _authorize_if_configured(
    app_id: str,
    api_token: str | None,
) -> dict[str, Any] | None:
    from deriv_sdk.client import DerivClient

    if api_token is None:
        return None

    client = DerivClient(app_id=app_id, api_token=api_token)
    try:
        async with asyncio.timeout(20):
            await client.start()
        return client.auth.authorize_response
    finally:
        await client.close()


async def main() -> None:
    app_id = _required_app_id()
    api_token = _optional_api_token()

    from deriv_sdk.client import DerivClient

    authorize_response = await _authorize_if_configured(app_id, api_token)
    client = DerivClient(app_id=app_id)

    try:
        async with asyncio.timeout(20):
            await client.start()

        active_symbols = await asyncio.wait_for(
            client.market.active_symbols(brief=False),
            timeout=20,
        )
        symbol = _select_symbol(active_symbols)

        history = await asyncio.wait_for(
            client.market.ticks_history(symbol.symbol, count=5),
            timeout=20,
        )
        trading_times = await asyncio.wait_for(
            client.market.trading_times(),
            timeout=20,
        )
        contracts = await asyncio.wait_for(
            client.market.contracts_for(symbol.symbol),
            timeout=20,
        )
        ticks = await asyncio.wait_for(
            _collect_ticks(client, symbol.symbol),
            timeout=40,
        )

        print("Live smoke test succeeded.")
        print(f"Connected: {client.connected}")
        print(f"Authorized: {authorize_response is not None}")
        print(f"Login ID: {_login_id(authorize_response)}")
        print(f"Selected symbol: {symbol.symbol}")
        print(f"Active symbols: {len(active_symbols)}")
        print(f"Tick history points: {_history_count(history)}")
        print(f"Trading markets: {_market_count(trading_times)}")
        print(f"Contracts available: {_contracts_count(contracts)}")
        print("Tick values: " + ", ".join(str(tick.quote) for tick in ticks))
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
