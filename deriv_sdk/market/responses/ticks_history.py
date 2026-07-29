"""
===========================================================
Deriv SDK

Ticks History Response

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from deriv_sdk.market.models import CandleHistory, TickHistory


class TicksHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @classmethod
    def parse_history(
        cls,
        obj: Any,
    ) -> TickHistory | CandleHistory:
        """
        Parse a Deriv ticks_history response.
        """

        if not isinstance(obj, dict):
            raise TypeError("Expected a dictionary.")

        # Tick history
        history = obj.get("history")
        if isinstance(history, dict):
            if "prices" in history:
                return TickHistory.model_validate(history)

            if "candles" in history:
                return CandleHistory.model_validate(history)

        # Candle history (top-level)
        if "candles" in obj:
            return CandleHistory.model_validate(obj)

        raise ValueError("Response does not contain tick or candle history.")
