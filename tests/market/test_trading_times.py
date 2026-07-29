"""
===========================================================
Deriv SDK

Tests - Trading Times

Version : 1.0.0
===========================================================
"""

import pytest

from deriv_sdk.market.exceptions import MarketError
from deriv_sdk.market.requests import TradingTimesRequest
from deriv_sdk.market.responses import TradingTimesResponse
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
# Request
# ==========================================================


def test_trading_times_request_default():

    request = TradingTimesRequest()

    assert request.to_dict() == {
        "trading_times": "today",
    }


def test_trading_times_request_date():

    request = TradingTimesRequest(
        date="2026-07-28",
    )

    assert request.to_dict() == {
        "trading_times": "2026-07-28",
    }


# ==========================================================
# Response
# ==========================================================


def test_trading_times_response():

    response = {
        "markets": [
            {
                "name": "Synthetic Indices",
                "submarkets": [
                    {
                        "name": "Random",
                        "symbols": [
                            {
                                "symbol": "R_100",
                                "events": [],
                                "trading_days": [
                                    {
                                        "open": "00:00",
                                        "close": "23:59",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    result = TradingTimesResponse.model_validate(response)

    assert len(result.markets) == 1
    assert result.markets[0].name == "Synthetic Indices"
    assert result.markets[0].submarkets[0].name == "Random"
    assert result.markets[0].submarkets[0].symbols[0].symbol == "R_100"


# ==========================================================
# Service
# ==========================================================


@pytest.mark.asyncio
async def test_trading_times_service():

    response = {
        "trading_times": {
            "markets": [
                {
                    "name": "Synthetic Indices",
                    "submarkets": [],
                }
            ]
        }
    }

    ws = MockWebSocket(response)

    service = MarketService(ws)

    result = await service.trading_times()

    assert ws.last_expected == "trading_times"

    assert ws.last_payload == {
        "trading_times": "today",
    }

    assert len(result.markets) == 1


@pytest.mark.asyncio
async def test_trading_times_error():

    ws = MockWebSocket(
        {
            "error": {
                "code": "InvalidRequest",
                "message": "Bad request",
            }
        }
    )

    service = MarketService(ws)

    with pytest.raises(MarketError):
        await service.trading_times()
