"""
===========================================================
Deriv SDK

Trade Models

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TradeResult(BaseModel):
    """
    Final result of an executed trade.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    proposal_id: str
    contract_id: int

    symbol: str
    contract_type: str

    stake: float

    buy_price: float

    sell_price: float | None = None

    profit: float | None = None

    payout: float | None = None

    status: str = "open"

    is_sold: bool = False

    is_won: bool | None = None
