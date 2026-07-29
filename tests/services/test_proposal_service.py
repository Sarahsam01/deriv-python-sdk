"""
===========================================================
Proposal Service Tests

Version : 1.0.0
===========================================================
"""

from unittest.mock import AsyncMock

import pytest

from deriv_sdk.models.proposal import Proposal
from deriv_sdk.trading.proposal_service import ProposalService


@pytest.fixture
def websocket():
    return AsyncMock()


@pytest.fixture
def service(websocket):
    return ProposalService(websocket)


@pytest.fixture
def proposal_response():
    return {
        "proposal": {
            "id": "12345",
            "ask_price": 1.25,
            "payout": 2.35,
            "spot": 1234.5,
            "display_value": 1.25,
            "currency": "USD",
            "contract_type": "CALL",
            "symbol": "R_100",
            "duration": 5,
            "duration_unit": "t",
            "longcode": "Sample proposal",
        }
    }


@pytest.mark.asyncio
async def test_request_proposal(
    service,
    websocket,
    proposal_response,
):
    websocket.request.return_value = proposal_response

    proposal = await service.request(
        symbol="R_100",
        contract_type="CALL",
        amount=1,
        duration=5,
        duration_unit="t",
    )

    assert isinstance(proposal, Proposal)

    assert proposal.id == "12345"

    websocket.request.assert_awaited_once()
