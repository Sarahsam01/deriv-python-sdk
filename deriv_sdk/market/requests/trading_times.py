"""
===========================================================
Deriv SDK

Trading Times Request

Responsibilities
----------------
• Build trading_times requests
• Validate request parameters

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TradingTimesRequest(BaseModel):
    """
    Request trading times from the Deriv API.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    date: str | None = None

    def to_dict(self) -> dict:
        """
        Convert request to Deriv API payload.
        """

        payload = {
            "trading_times": self.date or "today",
        }

        return payload
