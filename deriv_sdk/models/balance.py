"""
===========================================================
Deriv SDK

Balance Model

Represents an account balance returned by the Deriv API.

Version : 6.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Balance:
    """
    Represents a Deriv account balance.
    """

    balance: float
    currency: str
    loginid: str

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Balance:
        """
        Create a Balance instance from a Deriv API response.
        """

        balance = response["balance"]

        return cls(
            balance=float(balance["balance"]),
            currency=balance["currency"],
            loginid=balance["loginid"],
            raw=response,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """

        return {
            "balance": self.balance,
            "currency": self.currency,
            "loginid": self.loginid,
        }