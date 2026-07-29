"""
===========================================================
BuyResult Model Tests
===========================================================
"""

import pytest

from deriv_sdk.models.buy_result import BuyResult


def sample_response():
    return {
        "buy": {
            "contract_id": 10001,
            "transaction_id": 20002,
            "buy_price": 1.25,
            "balance_after": 98.75,
            "currency": "USD",
            "longcode": "Rise/Fall Contract",
            "start_time": 1700000000,
        }
    }


def test_buy_result_from_api():
    result = BuyResult.from_api(sample_response())

    assert result.contract_id == 10001
    assert result.transaction_id == 20002
    assert result.buy_price == 1.25
    assert result.balance_after == 98.75
    assert result.currency == "USD"


def test_buy_result_to_dict():
    result = BuyResult.from_api(sample_response())

    data = result.to_dict()

    assert data["contract_id"] == 10001
    assert data["transaction_id"] == 20002
    assert data["currency"] == "USD"


def test_buy_result_raw_response():
    result = BuyResult.from_api(sample_response())

    assert result.raw == sample_response()


def test_missing_buy_key():
    with pytest.raises(KeyError):
        BuyResult.from_api({})
