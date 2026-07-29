from unittest.mock import AsyncMock

import pytest

from deriv_sdk.models.transaction import Transaction
from deriv_sdk.trading.transaction_service import TransactionService


@pytest.fixture
def websocket():
    return AsyncMock()


@pytest.fixture
def service(websocket):
    return TransactionService(websocket)


@pytest.fixture
def transaction_response():
    return {
        "transaction": {
            "transaction_id": 987654321,
            "contract_id": 123456789,
            "action": "buy",
            "amount": -1.25,
            "balance": 998.75,
            "currency": "USD",
            "symbol": "R_100",
            "transaction_time": 1700000000,
        }
    }


@pytest.mark.asyncio
async def test_get_transaction(
    service,
    websocket,
    transaction_response,
):
    websocket.request.return_value = transaction_response

    transaction = await service.get(
        transaction_id=987654321,
    )

    assert isinstance(transaction, Transaction)

    assert transaction.transaction_id == 987654321
    assert transaction.contract_id == 123456789

    websocket.request.assert_awaited_once()
