"""
===========================================================
Contract Model Tests

Unit tests for the Contract model.

Version : 1.0.0
===========================================================
"""

import pytest

from deriv_sdk.models.contract import Contract


def sample_response():
    return {
        "proposal_open_contract": {
            "contract_id": 10001,
            "status": "open",
            "buy_price": 1.25,
            "payout": 2.35,
            "profit": 1.10,
            "entry_tick": 1234.5,
            "exit_tick": 1235.5,
            "currency": "USD",
            "symbol": "R_100",
            "contract_type": "CALL",
            "is_sold": False,
        }
    }


def test_contract_from_api():
    contract = Contract.from_api(sample_response())

    assert contract.contract_id == 10001
    assert contract.status == "open"
    assert contract.buy_price == 1.25
    assert contract.payout == 2.35
    assert contract.profit == 1.10
    assert contract.currency == "USD"
    assert contract.symbol == "R_100"


def test_contract_to_dict():
    contract = Contract.from_api(sample_response())

    data = contract.to_dict()

    assert data["contract_id"] == 10001
    assert data["status"] == "open"
    assert data["currency"] == "USD"


def test_contract_raw_response():
    contract = Contract.from_api(sample_response())

    assert contract.raw == sample_response()


def test_missing_contract_key():
    with pytest.raises(KeyError):
        Contract.from_api({})
