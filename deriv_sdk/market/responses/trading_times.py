"""
===========================================================
Deriv SDK

Trading Times Response

Responsibilities
----------------
• Parse trading_times responses

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TradingDay(BaseModel):
    """
    Trading schedule for a single day.
    """

    close: str = Field(description="Closing time.")
    open: str = Field(description="Opening time.")


class TradingSymbol(BaseModel):
    """
    Trading information for a symbol.
    """

    symbol: str
    events: list[dict] = Field(default_factory=list)
    trading_days: list[TradingDay] = Field(default_factory=list)


class TradingSubmarket(BaseModel):
    """
    Submarket information.
    """

    name: str
    symbols: list[TradingSymbol] = Field(default_factory=list)


class TradingMarket(BaseModel):
    """
    Market information.
    """

    name: str
    submarkets: list[TradingSubmarket] = Field(default_factory=list)


class TradingTimesResponse(BaseModel):
    """
    Response returned by the trading_times endpoint.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    markets: list[TradingMarket] = Field(default_factory=list)
