"""
===========================================================
Deriv SDK

Tests - Contracts For

Version : 1.0.0
===========================================================
"""

import pytest

from deriv_sdk.market.exceptions import MarketError
from deriv_sdk.market.models import ContractsFor
from deriv_sdk.market.requests import ContractsForRequest
from deriv_sdk.market.responses import ContractsForResponse
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

def test_contracts_for_request_defaults():

    request = ContractsForRequest(
        symbol="R_100",
    )

    assert request.to_dict() == {
        "contracts_for": "R_100",
        "product_type": "basic",
    }


def test_contracts_for_request_currency():

    request = ContractsForRequest(
        symbol="R_100",
        currency="USD",
    )

    assert request.to_dict() == {
        "contracts_for": "R_100",
        "currency": "USD",
        "product_type": "basic",
    }


# ==========================================================
# Response
# ==========================================================

def test_contracts_for_response():

    response = {
        "available": [
            {
                "contract_type": "CALL",
                "contract_display": "Rise",
                "market": "synthetic_index",
                "submarket": "random_index",
            }
        ]
    }

    result = ContractsForResponse.model_validate(response)

    assert isinstance(result, ContractsFor)

    assert result.count == 1

    assert result.available[0].contract_type == "CALL"

    assert result.available[0].contract_display == "Rise"


# ==========================================================
# Service
# ==========================================================

@pytest.mark.asyncio
async def test_contracts_for_service():

    response = {
        "contracts_for": {
            "available": [
                {
                    "contract_type": "CALL",
                    "contract_display": "Rise",
                }
            ]
        }
    }

    ws = MockWebSocket(response)

    service = MarketService(ws)

    result = await service.contracts_for(
        "R_100",
    )

    assert ws.last_expected == "contracts_for"

    assert ws.last_payload == {
        "contracts_for": "R_100",
        "product_type": "basic",
    }

    assert result.count == 1

    assert result.available[0].contract_type == "CALL"


@pytest.mark.asyncio
async def test_contracts_for_error():

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
        await service.contracts_for("INVALID")