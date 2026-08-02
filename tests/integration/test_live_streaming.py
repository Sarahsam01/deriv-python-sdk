from __future__ import annotations

import asyncio

import pytest

from deriv_sdk.client import DerivClient
from deriv_sdk.market.models import ActiveSymbol

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_live_tick_subscription(
    started_client: DerivClient,
    selected_symbol: ActiveSymbol,
) -> None:
    subscription = None
    try:
        async with asyncio.timeout(20):
            subscription = await started_client.market.subscribe_ticks(
                selected_symbol.symbol,
            )
            tick = await asyncio.wait_for(subscription.__anext__(), timeout=10)

        assert tick.symbol == selected_symbol.symbol
        assert isinstance(tick.quote, float)
    finally:
        if subscription is not None and not subscription.closed:
            async with asyncio.timeout(10):
                await subscription.unsubscribe()

    assert subscription is not None
    assert subscription.closed
