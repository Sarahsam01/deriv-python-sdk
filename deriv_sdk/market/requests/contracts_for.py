"""
===========================================================
Deriv SDK

Contracts For Request

Responsibilities
----------------
• Build contracts_for requests
• Validate parameters

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ContractsForRequest(BaseModel):
    """
    Request available contracts for a symbol.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    symbol: str
    currency: str | None = None
    product_type: str = "basic"

    def to_dict(self) -> dict:
        """
        Convert request into API payload.
        """

        payload = {
            "contracts_for": self.symbol,
            "product_type": self.product_type,
        }

        if self.currency:
            payload["currency"] = self.currency

        return payload
