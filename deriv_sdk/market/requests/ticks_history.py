"""
===========================================================
Deriv SDK

Ticks History Request

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TicksHistoryRequest(BaseModel):
    """
    Request historical ticks or candles.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    ticks_history: str

    adjust_start_time: int = 1

    count: int | None = None

    end: str | int = "latest"

    granularity: int | None = None

    start: int | None = None

    style: str = "ticks"

    def to_dict(self) -> dict:
        """
        Convert request to Deriv API payload.
        """

        payload = self.model_dump(
            exclude_none=True,
        )

        return payload
