from __future__ import annotations

import asyncio

import pytest

from deriv_sdk.client import DerivClient
from deriv_sdk.market.models import ActiveSymbol, CandleHistory, TickHistory

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_live_market_data(started_client: DerivClient) -> None:
    async with asyncio.timeout(30):
        active_symbols = await started_client.market.active_symbols(brief=False)

        if not active_symbols:
            pytest.skip("active_symbols returned no symbols for this live environment")


@pytest.mark.asyncio
async def test_live_symbol_market_data(
    started_client: DerivClient,
    selected_symbol: ActiveSymbol,
) -> None:
    async with asyncio.timeout(30):
        assert selected_symbol.symbol

        history = await started_client.market.ticks_history(
            selected_symbol.symbol,
            count=5,
        )
        assert isinstance(history, TickHistory | CandleHistory)
        assert history.count >= 1

        trading_times = await started_client.market.trading_times()
        assert trading_times.markets

        contracts = await started_client.market.contracts_for(selected_symbol.symbol)
        assert contracts.count >= 0
