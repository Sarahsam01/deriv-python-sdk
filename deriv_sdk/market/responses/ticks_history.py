"""
===========================================================
Deriv SDK

Ticks History Response

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import ConfigDict

from deriv_sdk.market.models import CandleHistory, TickHistory


class TicksHistoryResponse(TickHistory):
    """
    Response returned by the Deriv API when style="ticks".
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    history: TickHistory | None = None
    candles: CandleHistory | None = None

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        """
        Normalize Deriv API responses.

        Tick response:
            {
                "history": {
                    "prices": [...],
                    "times": [...]
                }
            }

        Candle response:
            {
                "candles": [...]
            }
        """

        if "history" in obj:
            return TickHistory.model_validate(obj["history"])

        if "candles" in obj:
            return CandleHistory.model_validate(
                {"candles": obj["candles"]}
            )

        return super().model_validate(obj, *args, **kwargs)