"""
===========================================================
Buy Service Tests

Version : 1.0.0
===========================================================
"""

from unittest.mock import AsyncMock

import pytest

from deriv_sdk.models.buy_result import BuyResult
from deriv_sdk.trading.buy_service import BuyService


@pytest.fixture
def websocket():
    return AsyncMock()


@pytest.fixture
def service(websocket):
    return BuyService(websocket)


@pytest.fixture
def buy_response():
    return {
        "buy": {
            "balance_after": 98.75,
            "buy_price": 1.25,
            "contract_id": 123456789,
            "longcode": "Sample contract",
            "payout": 2.35,
            "purchase_time": 1700000000,
            "shortcode": "CALL",
            "start_time": 1700000000,
            "transaction_id": 987654321,
        }
    }


@pytest.mark.asyncio
async def test_buy_contract(
    service,
    websocket,
    buy_response,
):
    websocket.request.return_value = buy_response

    result = await service.buy(
        proposal_id="12345",
        price=1.25,
    )

    assert isinstance(result, BuyResult)

    assert result.contract_id == 123456789
    assert result.buy_price == 1.25

    websocket.request.assert_awaited_once()
