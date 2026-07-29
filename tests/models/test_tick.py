import pytest

from deriv_sdk.models.tick import Tick


def test_tick_from_api():
    response = {
        "tick": {
            "symbol": "R_100",
            "quote": 1234.56,
            "epoch": 1722111111,
            "ask": 1234.57,
            "bid": 1234.55,
            "pip_size": 2,
            "id": "abc123",
        },
        "subscription": {
            "id": "sub001",
        },
    }

    tick = Tick.from_api(response)

    assert tick.symbol == "R_100"
    assert tick.quote == 1234.56
    assert tick.epoch == 1722111111
    assert tick.ask == 1234.57
    assert tick.bid == 1234.55
    assert tick.pip_size == 2
    assert tick.id == "abc123"
    assert tick.subscription_id == "sub001"


def test_tick_to_dict():
    tick = Tick(
        symbol="R_50",
        quote=987.65,
        epoch=1722000000,
    )

    data = tick.to_dict()

    assert data["symbol"] == "R_50"
    assert data["quote"] == 987.65
    assert data["epoch"] == 1722000000


def test_tick_repr():
    tick = Tick(
        symbol="R_25",
        quote=100.25,
        epoch=1234567890,
    )

    text = repr(tick)

    assert "Tick" in text
    assert "R_25" in text


@pytest.mark.parametrize(
    "quote",
    [0.0, 1.23, 99999.99],
)
def test_tick_quote_values(quote):
    tick = Tick(
        symbol="TEST",
        quote=quote,
        epoch=1,
    )

    assert tick.quote == quote