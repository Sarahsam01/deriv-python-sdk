"""
===========================================================
Deriv SDK

Trading Request Base

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TradingRequest(BaseModel):
    """
    Base class for all trading requests.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    def to_dict(self) -> dict[str, object]:
        """
        Convert request into API payload.
        """
        return self.model_dump(
            exclude_none=True,
        )