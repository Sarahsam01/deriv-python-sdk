from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest

from deriv_sdk.client import DerivClient
from deriv_sdk.config import SDKConfig
from deriv_sdk.market.models import ActiveSymbol


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    marker_expression = config.option.markexpr or ""
    if "integration" in marker_expression:
        return

    skip_integration = pytest.mark.skip(
        reason="live integration tests run only with -m integration",
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def app_id() -> str:
    value = os.getenv("DERIV_APP_ID", "").strip()
    if not value:
        pytest.skip("DERIV_APP_ID is required for live integration tests")
    return value


@pytest.fixture
def api_token() -> str | None:
    value = os.getenv("DERIV_API_TOKEN", "").strip()
    return value or None


@pytest.fixture
def sdk_config(app_id: str, api_token: str | None) -> SDKConfig:
    return SDKConfig(
        app_id=app_id,
        api_token=api_token or "",
    )


@pytest.fixture
async def client(sdk_config: SDKConfig) -> AsyncIterator[DerivClient]:
    live_client = DerivClient(
        app_id=sdk_config.app_id,
    )
    try:
        yield live_client
    finally:
        await live_client.close()


def select_live_symbol(symbols: list[ActiveSymbol]) -> ActiveSymbol:
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
        pytest.skip("active_symbols returned no symbols for this live environment")

    return candidates[0]


@pytest.fixture
async def started_client(client: DerivClient) -> AsyncIterator[DerivClient]:
    await client.start()
    yield client


@pytest.fixture
async def selected_symbol(started_client: DerivClient) -> ActiveSymbol:
    symbols = await started_client.market.active_symbols(brief=False)
    return select_live_symbol(symbols)
