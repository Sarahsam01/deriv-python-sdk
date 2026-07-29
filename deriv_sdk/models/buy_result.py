"""
===========================================================
Deriv SDK

Buy Result Model

Represents a successful BUY response returned by Deriv.

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BuyResult:
    """
    Represents a successful contract purchase.
    """

    contract_id: int
    transaction_id: int
    buy_price: float
    balance_after: float
    currency: str
    longcode: str
    start_time: int

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> BuyResult:
        """
        Create a BuyResult instance from a Deriv API response.
        """

        buy = response["buy"]

        return cls(
            contract_id=int(buy["contract_id"]),
            transaction_id=int(buy["transaction_id"]),
            buy_price=float(buy["buy_price"]),
            balance_after=float(buy["balance_after"]),
            currency=buy.get("currency", ""),
            longcode=buy.get("longcode", ""),
            start_time=int(buy.get("start_time", 0)),
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "contract_id": self.contract_id,
            "transaction_id": self.transaction_id,
            "buy_price": self.buy_price,
            "balance_after": self.balance_after,
            "currency": self.currency,
            "longcode": self.longcode,
            "start_time": self.start_time,
        }

    def __repr__(self) -> str:
        return (
            f"BuyResult("
            f"contract_id={self.contract_id}, "
            f"transaction_id={self.transaction_id}, "
            f"buy_price={self.buy_price}, "
            f"balance_after={self.balance_after}, "
            f"currency={self.currency!r})"
        )