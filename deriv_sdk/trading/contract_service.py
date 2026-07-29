"""
===========================================================
Deriv SDK

Contract Service

Responsibilities
----------------
• Validate contract requests
• Build contract payloads
• Retrieve contract information
• Parse contract responses
• Return Contract models

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.models.contract import Contract
from deriv_sdk.trading.base_service import BaseTradingService
from deriv_sdk.transport.websocket import WebSocketClient


class ContractService(BaseTradingService[Contract]):
    """
    Service responsible for retrieving contract information.
    """

    def __init__(
        self,
        websocket: WebSocketClient,
    ) -> None:
        super().__init__(websocket)

    async def get(
        self,
        *,
        contract_id: int,
    ) -> Contract:
        """
        Retrieve information about an existing contract.
        """

        self._validate_request(contract_id=contract_id)

        payload = self._build_request(contract_id=contract_id)

        return await self._execute(
            payload=payload,
            expected="proposal_open_contract",
        )

    def _validate_request(
        self,
        *,
        contract_id: int,
    ) -> None:
        """
        Validate contract request parameters.
        """

        if contract_id <= 0:
            raise ValueError("contract_id must be greater than zero.")

    def _build_request(
        self,
        *,
        contract_id: int,
    ) -> dict[str, object]:
        """
        Build a contract request payload.
        """

        return {
            "proposal_open_contract": 1,
            "contract_id": contract_id,
        }

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> Contract:
        """
        Convert the API response into a Contract model.
        """

        return Contract.from_api(response)
