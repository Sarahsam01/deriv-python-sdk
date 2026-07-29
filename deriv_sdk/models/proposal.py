"""
===========================================================
Deriv SDK

Proposal Model

Represents a proposal returned by the Deriv API.

Version : 6.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Proposal:
    """
    Represents a Deriv proposal returned by the API.

    A proposal is a quotation for a potential trade.
    """

    id: str
    ask_price: float
    payout: float
    spot: float
    display_value: float
    currency: str
    contract_type: str
    symbol: str
    duration: int
    duration_unit: str
    longcode: str

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Proposal:
        """
        Create a Proposal instance from a Deriv API response.
        """

        proposal = response["proposal"]

        return cls(
            id=proposal["id"],
            ask_price=float(proposal["ask_price"]),
            payout=float(proposal["payout"]),
            spot=float(proposal["spot"]),
            display_value=float(proposal["display_value"]),
            currency=proposal["currency"],
            contract_type=proposal["contract_type"],
            symbol=proposal["symbol"],
            duration=int(proposal["duration"]),
            duration_unit=proposal["duration_unit"],
            longcode=proposal["longcode"],
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "id": self.id,
            "ask_price": self.ask_price,
            "payout": self.payout,
            "spot": self.spot,
            "display_value": self.display_value,
            "currency": self.currency,
            "contract_type": self.contract_type,
            "symbol": self.symbol,
            "duration": self.duration,
            "duration_unit": self.duration_unit,
            "longcode": self.longcode,
        }

    def __repr__(self) -> str:
        return (
            f"Proposal("
            f"id={self.id!r}, "
            f"symbol={self.symbol!r}, "
            f"contract_type={self.contract_type!r}, "
            f"ask_price={self.ask_price}, "
            f"payout={self.payout})"
        )
