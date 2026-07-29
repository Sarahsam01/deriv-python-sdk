"""
===========================================================
Deriv SDK

Tests - Market Service

Version : 1.0.0
===========================================================
"""

import pytest

from deriv_sdk.market.exceptions import MarketError
from deriv_sdk.market.models import (
    CandleHistory,
    TickHistory,
)
from deriv_sdk.market.service import MarketService


class MockWebSocket:
    """
    Mock websocket transport.
    """

    def __init__(self, response):
        self.response = response
        self.last_payload = None
        self.last_expected = None

    async def request(self, payload, expected):
        self.last_payload = payload
        self.last_expected = expected
        return self.response


# ==========================================================
# Active Symbols
# ==========================================================

@pytest.mark.asyncio
async def test_active_symbols_success():

    response = {
        "active_symbols": [
            {
                "symbol": "R_100",
                "display_name": "Volatility 100 Index",
                "market": "synthetic_index",
                "market_display_name": "Synthetic Indices",
                "submarket": "random_index",
                "submarket_display_name": "Random",
                "exchange_is_open": 1,
                "is_trading_suspended": 0,
            }
        ]
    }

    ws = MockWebSocket(response)

    service = MarketService(ws)

    result = await service.active_symbols()

    assert len(result) == 1

    assert ws.last_expected == "active_symbols"

    assert ws.last_payload == {
        "active_symbols": "brief"
    }


# ==========================================================
# Tick History
# ==========================================================

@pytest.mark.asyncio
async def test_tick_history_success():

    response = {
        "history": {
            "prices": [100, 101, 102],
            "times": [1, 2, 3],
        }
    }

    ws = MockWebSocket(response)

    service = MarketService(ws)

    history = await service.ticks_history("R_100")

    assert isinstance(history, TickHistory)

    assert history.count == 3

    assert ws.last_expected == "history"

    assert ws.last_payload["ticks_history"] == "R_100"


# ==========================================================
# Candle History
# ==========================================================

@pytest.mark.asyncio
async def test_candle_history_success():

    response = {
        "candles": [
            {
                "epoch": 1,
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100.5,
            }
        ]
    }

    ws = MockWebSocket(response)

    service = MarketService(ws)

    candles = await service.ticks_history(
        "R_100",
        style="candles",
        granularity=60,
    )

    assert isinstance(candles, CandleHistory)

    assert candles.count == 1

    assert candles.candles[0].close == 100.5


# ==========================================================
# API Errors
# ==========================================================

@pytest.mark.asyncio
async def test_market_error():

    ws = MockWebSocket(
        {
            "error": {
                "code": "InvalidSymbol",
                "message": "Invalid symbol",
            }
        }
    )

    service = MarketService(ws)

    with pytest.raises(MarketError):
        await service.ticks_history("INVALID")