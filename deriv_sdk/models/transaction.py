"""
===========================================================
Deriv SDK

Transaction Model

Represents a transaction returned by the Deriv API.

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Transaction:
    """
    Represents a Deriv account transaction.
    """

    transaction_id: int
    contract_id: int
    action: str
    amount: float
    balance: float
    currency: str
    symbol: str
    transaction_time: int

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Transaction:
        """
        Create a Transaction instance from a Deriv API response.
        """

        tx = response["transaction"]

        return cls(
            transaction_id=int(tx["transaction_id"]),
            contract_id=int(tx.get("contract_id", 0)),
            action=tx.get("action", ""),
            amount=float(tx.get("amount", 0.0)),
            balance=float(tx.get("balance", 0.0)),
            currency=tx.get("currency", ""),
            symbol=tx.get("symbol", ""),
            transaction_time=int(tx.get("transaction_time", 0)),
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "transaction_id": self.transaction_id,
            "contract_id": self.contract_id,
            "action": self.action,
            "amount": self.amount,
            "balance": self.balance,
            "currency": self.currency,
            "symbol": self.symbol,
            "transaction_time": self.transaction_time,
        }

    def __repr__(self) -> str:
        return (
            f"Transaction("
            f"transaction_id={self.transaction_id}, "
            f"action={self.action!r}, "
            f"amount={self.amount}, "
            f"balance={self.balance})"
        )
