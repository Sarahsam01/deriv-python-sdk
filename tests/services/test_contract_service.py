from unittest.mock import AsyncMock

import pytest

from deriv_sdk.models.contract import Contract
from deriv_sdk.trading.contract_service import ContractService


@pytest.fixture
def websocket():
    return AsyncMock()


@pytest.fixture
def service(websocket):
    return ContractService(websocket)


@pytest.fixture
def contract_response():
    return {
        "proposal_open_contract": {
            "contract_id": 123456789,
            "buy_price": 1.25,
            "sell_price": 2.35,
            "profit": 1.10,
            "status": "won",
            "is_sold": 1,
            "currency": "USD",
            "symbol": "R_100",
            "longcode": "Sample contract",
        }
    }


@pytest.mark.asyncio
async def test_get_contract(
    service,
    websocket,
    contract_response,
):
    websocket.request.return_value = contract_response

    contract = await service.get(
        contract_id=123456789,
    )

    assert isinstance(contract, Contract)
    assert contract.contract_id == 123456789

    websocket.request.assert_awaited_once()