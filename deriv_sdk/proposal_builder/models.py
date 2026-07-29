"""
===========================================================
Deriv SDK

Proposal Builder Models

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Proposal(BaseModel):
    """
    Complete proposal request.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    amount: float
    basis: str = "stake"
    contract_type: str
    currency: str = "USD"
    duration: int
    duration_unit: str = "t"
    symbol: str

    barrier: str | None = None

    prediction: int | None = None

    def to_dict(self) -> dict:
        payload = self.model_dump(exclude_none=True)
        payload["proposal"] = 1
        return payload