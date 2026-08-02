"""
===========================================================
Deriv SDK

Transaction Service

Responsibilities
----------------
• Retrieve transaction information
• Parse transaction responses
• Return Transaction models

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.models.transaction import Transaction
from deriv_sdk.request.engine import RequestEngine
from deriv_sdk.trading.base_service import BaseTradingService
from deriv_sdk.transport.websocket import WebSocketClient


class TransactionService(BaseTradingService[Transaction]):
    """Service responsible for retrieving transaction information."""

    def __init__(self, websocket: WebSocketClient | RequestEngine) -> None:
        """
        Create a transaction service.

        Parameters
        ----------
        websocket:
            Shared request engine or compatible transport.
        """
        super().__init__(websocket)

    async def get(self, *, transaction_id: int) -> Transaction:
        """
        Retrieve a transaction by id.

        Parameters
        ----------
        transaction_id:
            Positive Deriv transaction identifier.

        Returns
        -------
        Transaction
            Parsed transaction model.

        Raises
        ------
        ValueError
            If ``transaction_id`` is not positive.
        """
        if transaction_id <= 0:
            raise ValueError("transaction_id must be greater than zero.")

        payload = {
            "transaction": 1,
            "transaction_id": transaction_id,
        }

        return await self._execute(
            payload=payload,
            expected="transaction",
        )

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> Transaction:
        """Convert the API response into a Transaction model."""
        return Transaction.from_api(response)
