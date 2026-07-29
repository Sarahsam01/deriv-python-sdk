"""
============================================================
Deriv SDK

Tick Model

Represents a live market tick returned by the Deriv API.

Author : OpenAI
Version: 1.0.0
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Tick:
    """
    Live market tick.
    """

    symbol: str
    quote: float
    epoch: int
    ask: float | None = None
    bid: float | None = None
    pip_size: int | None = None
    id: str | None = None
    subscription_id: str | None = None

    @classmethod
    def from_api(cls, response: dict[str, Any]) -> Tick:
        """
        Build a Tick from a Deriv API response.
        """

        tick = response["tick"]

        subscription = response.get("subscription", {})

        return cls(
            symbol=tick["symbol"],
            quote=float(tick["quote"]),
            epoch=int(tick["epoch"]),
            ask=float(tick["ask"]) if tick.get("ask") is not None else None,
            bid=float(tick["bid"]) if tick.get("bid") is not None else None,
            pip_size=tick.get("pip_size"),
            id=tick.get("id"),
            subscription_id=subscription.get("id"),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary.
        """

        return {
            "symbol": self.symbol,
            "quote": self.quote,
            "epoch": self.epoch,
            "ask": self.ask,
            "bid": self.bid,
            "pip_size": self.pip_size,
            "id": self.id,
            "subscription_id": self.subscription_id,
        }

    def __repr__(self) -> str:
        return (
            "Tick("
            f"symbol='{self.symbol}', "
            f"quote={self.quote}, "
            f"epoch={self.epoch})"
        )