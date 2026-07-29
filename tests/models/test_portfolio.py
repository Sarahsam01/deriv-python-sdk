"""
===========================================================
Portfolio Model Tests
===========================================================
"""

import pytest

from deriv_sdk.models.portfolio import Portfolio


def sample_response():
    return {
        "portfolio": {
            "contract_id": 10001,
            "contract_type": "CALL",
            "symbol": "R_100",
            "buy_price": 1.25,
            "payout": 2.35,
            "profit": 1.10,
            "currency": "USD",
            "status": "open",
            "purchase_time": 1700000000,
        }
    }


def test_portfolio_from_api():
    portfolio = Portfolio.from_api(sample_response())

    assert portfolio.contract_id == 10001
    assert portfolio.contract_type == "CALL"
    assert portfolio.symbol == "R_100"
    assert portfolio.buy_price == 1.25
    assert portfolio.currency == "USD"


def test_portfolio_to_dict():
    portfolio = Portfolio.from_api(sample_response())

    data = portfolio.to_dict()

    assert data["contract_id"] == 10001
    assert data["status"] == "open"


def test_portfolio_raw_response():
    portfolio = Portfolio.from_api(sample_response())

    assert portfolio.raw == sample_response()


def test_missing_portfolio_key():
    with pytest.raises(KeyError):
        Portfolio.from_api({})
