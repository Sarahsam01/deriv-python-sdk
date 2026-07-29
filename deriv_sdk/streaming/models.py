"""
===========================================================
Deriv SDK

Streaming Models

Responsibilities
----------------
• Tick model
• Tick stream model
• Base streaming models

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import ConfigDict, Field

from deriv_sdk.market.models import MarketModel


class Tick(MarketModel):
    """
    Represents a live market tick.
    """

    symbol: str = Field(description="Market symbol.")

    quote: float = Field(description="Latest price.")

    epoch: int = Field(description="Unix timestamp.")

    id: str | None = Field(default=None, description="Tick identifier.")

    pip_size: int | None = Field(default=None, description="Decimal precision.")

    ask: float | None = Field(default=None, description="Ask price.")

    bid: float | None = Field(default=None, description="Bid price.")

    def __str__(self) -> str:
        return f"{self.symbol} {self.quote}"


class TickResponse(MarketModel):
    """
    Response returned by a tick subscription.
    """

    model_config = ConfigDict(
        extra="allow",
    )

    tick: Tick

    msg_type: str

    subscription: dict | None = None

    echo_req: dict | None = None

    req_id: int | None = None


class TickHistoryItem(MarketModel):
    """
    Represents one historical tick.
    """

    epoch: int

    quote: float


class TickHistory(MarketModel):
    """
    Historical tick collection.
    """

    symbol: str

    prices: list[TickHistoryItem] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.prices)

    def __iter__(self):
        return iter(self.prices)

    def __getitem__(self, index: int):
        return self.prices[index]
