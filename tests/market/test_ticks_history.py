"""
===========================================================
Deriv SDK

Tests - Market History

Version : 1.0.0
===========================================================
"""

from deriv_sdk.market.models import (
    CandleHistory,
    TickHistory,
)
from deriv_sdk.market.requests import TicksHistoryRequest
from deriv_sdk.market.responses import TicksHistoryResponse


def test_ticks_history_request_defaults():
    request = TicksHistoryRequest(
        ticks_history="R_100",
    )

    payload = request.to_dict()

    assert payload["ticks_history"] == "R_100"
    assert payload["style"] == "ticks"
    assert payload["end"] == "latest"
    assert payload["adjust_start_time"] == 1


def test_ticks_history_request_with_parameters():
    request = TicksHistoryRequest(
        ticks_history="R_50",
        count=500,
        start=1000,
        end=2000,
        granularity=60,
        style="candles",
    )

    payload = request.to_dict()

    assert payload["ticks_history"] == "R_50"
    assert payload["count"] == 500
    assert payload["start"] == 1000
    assert payload["end"] == 2000
    assert payload["granularity"] == 60
    assert payload["style"] == "candles"


def test_tick_history_response():
    response = {
        "history": {
            "prices": [100.1, 100.2, 100.3],
            "times": [1, 2, 3],
        }
    }

    history = TicksHistoryResponse.model_validate(response)

    assert isinstance(history, TickHistory)
    assert history.count == 3
    assert history.prices[0] == 100.1
    assert history.times[2] == 3


def test_candle_history_response():
    response = {
        "candles": [
            {
                "epoch": 1,
                "open": 100,
                "high": 110,
                "low": 95,
                "close": 105,
            },
            {
                "epoch": 2,
                "open": 105,
                "high": 112,
                "low": 101,
                "close": 110,
            },
        ]
    }

    history = TicksHistoryResponse.model_validate(response)

    assert isinstance(history, CandleHistory)
    assert history.count == 2

    candle = history.candles[0]

    assert candle.open == 100
    assert candle.high == 110
    assert candle.low == 95
    assert candle.close == 105