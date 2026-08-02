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
from deriv_sdk.market.requests import ActiveSymbolsRequest
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
        "active_symbols": "brief",
        "product_type": "basic",
    }


def test_active_symbols_request_defaults():
    request = ActiveSymbolsRequest()

    assert request.to_dict() == {
        "active_symbols": "brief",
        "product_type": "basic",
    }


def test_active_symbols_request_full():
    request = ActiveSymbolsRequest(brief=False)

    assert request.to_dict() == {
        "active_symbols": "full",
        "product_type": "basic",
    }


def test_active_symbols_request_omits_none_fields():
    request = ActiveSymbolsRequest(
        product_type=None,
        landing_company_short=None,
    )

    assert request.to_dict() == {"active_symbols": "brief"}


def test_active_symbols_request_landing_company():
    request = ActiveSymbolsRequest(
        product_type="basic",
        landing_company_short="svg",
    )

    assert request.to_dict() == {
        "active_symbols": "brief",
        "product_type": "basic",
        "landing_company_short": "svg",
    }


@pytest.mark.asyncio
async def test_active_symbols_service_options():
    response = {"active_symbols": []}
    ws = MockWebSocket(response)
    service = MarketService(ws)

    result = await service.active_symbols(
        brief=False,
        product_type="basic",
        landing_company_short="svg",
    )

    assert result == []
    assert ws.last_payload == {
        "active_symbols": "full",
        "product_type": "basic",
        "landing_company_short": "svg",
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
