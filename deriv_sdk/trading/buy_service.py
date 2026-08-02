"""
===========================================================
Deriv SDK

Buy Service

Responsibilities
----------------
• Validate buy requests
• Build buy payloads
• Execute contract purchases
• Parse buy responses
• Return BuyResult models

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.models.buy_result import BuyResult
from deriv_sdk.request.engine import RequestEngine
from deriv_sdk.trading.base_service import BaseTradingService
from deriv_sdk.transport.websocket import WebSocketClient


class BuyService(BaseTradingService[BuyResult]):
    """
    Service responsible for purchasing contracts using
    an existing proposal.
    """

    def __init__(
        self,
        websocket: WebSocketClient | RequestEngine,
    ) -> None:
        super().__init__(websocket)

    async def buy(
        self,
        *,
        proposal_id: str,
        price: float,
    ) -> BuyResult:
        """
        Execute a contract purchase.
        """

        self._validate_request(
            proposal_id=proposal_id,
            price=price,
        )

        payload = self._build_request(
            proposal_id=proposal_id,
            price=price,
        )

        return await self._execute(
            payload=payload,
            expected="buy",
        )

    def _validate_request(
        self,
        *,
        proposal_id: str,
        price: float,
    ) -> None:
        """
        Validate buy request parameters.
        """

        if not proposal_id.strip():
            raise ValueError("proposal_id is required.")

        if price <= 0:
            raise ValueError("price must be greater than zero.")

    def _build_request(
        self,
        *,
        proposal_id: str,
        price: float,
    ) -> dict[str, object]:
        """
        Build a buy request payload.
        """

        return {
            "buy": proposal_id,
            "price": price,
        }

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> BuyResult:
        """
        Convert the API response into a BuyResult model.
        """

        return BuyResult.from_api(response)
