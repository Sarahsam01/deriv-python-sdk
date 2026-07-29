from unittest.mock import AsyncMock

import pytest

from deriv_sdk.models.balance import Balance
from deriv_sdk.trading.balance_service import BalanceService


@pytest.fixture
def websocket():
    return AsyncMock()


@pytest.fixture
def service(websocket):
    return BalanceService(websocket)


@pytest.fixture
def balance_response():
    return {
        "balance": {
            "balance": 1000.25,
            "currency": "USD",
            "loginid": "CR123456",
        }
    }


@pytest.mark.asyncio
async def test_get_balance(
    service,
    websocket,
    balance_response,
):
    websocket.request.return_value = balance_response

    balance = await service.get()

    assert isinstance(balance, Balance)

    assert balance.balance == 1000.25
    assert balance.currency == "USD"

    websocket.request.assert_awaited_once()