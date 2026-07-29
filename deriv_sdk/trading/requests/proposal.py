"""
===========================================================
Deriv SDK

Proposal Request

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from .base import TradingRequest


class ProposalRequest(TradingRequest):
    """
    Proposal request payload.
    """

    symbol: str

    contract_type: str

    amount: float

    basis: str = "stake"

    currency: str = "USD"

    duration: int = 1

    duration_unit: str = "t"

    barrier: str | None = None

    prediction: int | None = None

    def to_dict(self) -> dict[str, object]:
        payload = super().to_dict()
        payload["proposal"] = 1
        return payload
