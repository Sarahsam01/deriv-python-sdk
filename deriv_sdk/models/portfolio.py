"""
===========================================================
Deriv SDK

Portfolio Model

Represents an open contract in the user's portfolio.

Version : 6.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Portfolio:
    """
    Represents an open contract in the user's portfolio.
    """

    contract_id: int
    contract_type: str
    symbol: str
    buy_price: float
    payout: float
    profit: float
    currency: str
    status: str
    purchase_time: int

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Portfolio:
        """
        Create a Portfolio instance from a Deriv API response.
        """

        portfolio = response["portfolio"]

        return cls(
            contract_id=int(portfolio["contract_id"]),
            contract_type=portfolio["contract_type"],
            symbol=portfolio["symbol"],
            buy_price=float(portfolio["buy_price"]),
            payout=float(portfolio["payout"]),
            profit=float(portfolio["profit"]),
            currency=portfolio["currency"],
            status=portfolio["status"],
            purchase_time=int(portfolio["purchase_time"]),
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "symbol": self.symbol,
            "buy_price": self.buy_price,
            "payout": self.payout,
            "profit": self.profit,
            "currency": self.currency,
            "status": self.status,
            "purchase_time": self.purchase_time,
        }
