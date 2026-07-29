"""
===========================================================
Deriv SDK

Contract Model

Represents a contract returned by the Deriv API.

Version : 7.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Contract:
    """
    Represents a Deriv contract returned by the API.
    """

    contract_id: int
    transaction_id: int
    status: str
    is_sold: bool
    buy_price: float
    payout: float
    profit: float
    bid_price: float
    sell_price: float
    currency: str
    symbol: str
    contract_type: str
    entry_tick: float
    exit_tick: float | None
    entry_time: int
    exit_time: int | None
    longcode: str

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Contract:
        """
        Create a Contract instance from a Deriv API response.
        """

        contract = response["proposal_open_contract"]

        return cls(
            contract_id=int(contract["contract_id"]),
            transaction_id=int(contract.get("transaction_id", 0)),
            status=contract.get("status", ""),
            is_sold=bool(contract.get("is_sold", False)),
            buy_price=float(contract.get("buy_price", 0.0)),
            payout=float(contract.get("payout", 0.0)),
            profit=float(contract.get("profit", 0.0)),
            bid_price=float(contract.get("bid_price", 0.0)),
            sell_price=float(contract.get("sell_price", 0.0)),
            currency=contract.get("currency", ""),
            symbol=contract.get("symbol", ""),
            contract_type=contract.get("contract_type", ""),
            entry_tick=float(contract.get("entry_tick", 0.0)),
            exit_tick=(
                float(contract["exit_tick"])
                if contract.get("exit_tick") is not None
                else None
            ),
            entry_time=int(contract.get("entry_time", 0)),
            exit_time=(
                int(contract["exit_time"])
                if contract.get("exit_time") is not None
                else None
            ),
            longcode=contract.get("longcode", ""),
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "contract_id": self.contract_id,
            "transaction_id": self.transaction_id,
            "status": self.status,
            "is_sold": self.is_sold,
            "buy_price": self.buy_price,
            "payout": self.payout,
            "profit": self.profit,
            "bid_price": self.bid_price,
            "sell_price": self.sell_price,
            "currency": self.currency,
            "symbol": self.symbol,
            "contract_type": self.contract_type,
            "entry_tick": self.entry_tick,
            "exit_tick": self.exit_tick,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "longcode": self.longcode,
        }

    def __repr__(self) -> str:
        return (
            f"Contract("
            f"contract_id={self.contract_id}, "
            f"status={self.status!r}, "
            f"profit={self.profit}, "
            f"symbol={self.symbol!r}, "
            f"contract_type={self.contract_type!r})"
        )
