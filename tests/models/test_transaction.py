"""
===========================================================
Transaction Model Tests
===========================================================
"""

import pytest

from deriv_sdk.models.transaction import Transaction


def sample_response():
    return {
        "transaction": {
            "transaction_id": 123456,
            "action": "buy",
            "amount": 1.25,
            "balance": 98.75,
            "currency": "USD",
            "symbol": "R_100",
            "contract_id": 987654,
            "transaction_time": 1700000000,
        }
    }


def test_transaction_from_api():
    transaction = Transaction.from_api(sample_response())

    assert transaction.transaction_id == 123456
    assert transaction.action == "buy"
    assert transaction.amount == 1.25
    assert transaction.balance == 98.75
    assert transaction.currency == "USD"
    assert transaction.symbol == "R_100"
    assert transaction.contract_id == 987654
    assert transaction.transaction_time == 1700000000


def test_transaction_to_dict():
    transaction = Transaction.from_api(sample_response())

    data = transaction.to_dict()

    assert data["transaction_id"] == 123456
    assert data["action"] == "buy"
    assert data["currency"] == "USD"


def test_transaction_raw_response():
    transaction = Transaction.from_api(sample_response())

    assert transaction.raw == sample_response()


def test_missing_transaction_key():
    with pytest.raises(KeyError):
        Transaction.from_api({})
