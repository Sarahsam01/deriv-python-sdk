"""
===========================================================
Balance Model Tests
===========================================================
"""

import pytest

from deriv_sdk.models.balance import Balance


def sample_response():
    return {
        "balance": {
            "balance": 125.75,
            "currency": "USD",
            "loginid": "CR123456",
        }
    }


def test_balance_from_api():
    result = Balance.from_api(sample_response())

    assert result.balance == 125.75
    assert result.currency == "USD"
    assert result.loginid == "CR123456"


def test_balance_to_dict():
    result = Balance.from_api(sample_response())

    data = result.to_dict()

    assert data["balance"] == 125.75
    assert data["currency"] == "USD"
    assert data["loginid"] == "CR123456"


def test_balance_raw_response():
    result = Balance.from_api(sample_response())

    assert result.raw == sample_response()


def test_missing_balance_key():
    with pytest.raises(KeyError):
        Balance.from_api({})
