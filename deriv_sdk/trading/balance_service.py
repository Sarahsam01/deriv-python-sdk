"""
===========================================================
Deriv SDK

Balance Service

Responsibilities
----------------
• Request account balance
• Parse balance responses
• Return Balance models

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.models.balance import Balance
from deriv_sdk.trading.base_service import BaseTradingService
from deriv_sdk.transport.websocket import WebSocketClient


class BalanceService(BaseTradingService[Balance]):
    """
    Service responsible for retrieving the account balance.
    """

    def __init__(
        self,
        websocket: WebSocketClient,
    ) -> None:
        super().__init__(websocket)

    async def get(self) -> Balance:
        """
        Retrieve the current account balance.
        """

        payload = {
            "balance": 1,
        }

        return await self._execute(
            payload=payload,
            expected="balance",
        )

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> Balance:
        """
        Convert the API response into a Balance model.
        """

        return Balance.from_api(response)