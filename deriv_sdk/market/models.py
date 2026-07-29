"""
===========================================================
Deriv SDK

Market Models

Responsibilities
----------------
• Shared market models
• Active symbol model
• Historical tick models
• Candle models
• Contract models
• Base model for future market endpoints

Version : 2.2.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MarketModel(BaseModel):
    """
    Base class for all market models.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )


# ===========================================================
# Active Symbols
# ===========================================================


class ActiveSymbol(MarketModel):
    """
    Represents a tradable market symbol.
    """

    symbol: str = Field(description="Internal market symbol.")

    display_name: str = Field(description="Display name.")

    market: str = Field(description="Market category.")

    market_display_name: str = Field(description="Market display name.")

    submarket: str = Field(description="Submarket.")

    submarket_display_name: str = Field(description="Submarket display name.")

    exchange_is_open: int = Field(description="Exchange open flag.")

    is_trading_suspended: int = Field(description="Trading suspension flag.")

    display_order: int | None = Field(
        default=None,
        description="Display order.",
    )

    pip: float | None = Field(
        default=None,
        description="Minimum price increment.",
    )

    symbol_type: str | None = Field(
        default=None,
        description="Symbol type.",
    )

    allow_forward_starting: int | None = Field(
        default=None,
        description="Forward-start availability.",
    )

    exchange_name: str | None = Field(
        default=None,
        description="Exchange name.",
    )

    is_market_closed: int | None = Field(
        default=None,
        description="Market closed flag.",
    )

    settlement_interval: int | None = Field(
        default=None,
        description="Settlement interval.",
    )

    def __str__(self) -> str:
        return f"{self.symbol} ({self.display_name})"

    @property
    def is_open(self) -> bool:
        """
        True if the market is open.
        """
        return bool(self.exchange_is_open)

    @property
    def is_suspended(self) -> bool:
        """
        True if trading is suspended.
        """
        return bool(self.is_trading_suspended)


# ===========================================================
# Historical Tick Models
# ===========================================================


class TickHistory(MarketModel):
    """
    Historical tick data returned by the Deriv API.
    """

    prices: list[float] = Field(
        default_factory=list,
        description="Historical prices.",
    )

    times: list[int] = Field(
        default_factory=list,
        description="Unix timestamps.",
    )

    @property
    def count(self) -> int:
        """
        Number of historical ticks.
        """
        return len(self.prices)


# ===========================================================
# Candle Models
# ===========================================================


class Candle(MarketModel):
    """
    Represents a single OHLC candle.
    """

    epoch: int = Field(description="Unix timestamp.")

    open: float = Field(description="Opening price.")

    high: float = Field(description="Highest price.")

    low: float = Field(description="Lowest price.")

    close: float = Field(description="Closing price.")


class CandleHistory(MarketModel):
    """
    Historical candle data.
    """

    candles: list[Candle] = Field(
        default_factory=list,
        description="Historical candles.",
    )

    @property
    def count(self) -> int:
        """
        Number of candles.
        """
        return len(self.candles)


# ===========================================================
# Contract Models
# ===========================================================


class Contract(MarketModel):
    """
    Represents a contract available for a market symbol.
    """

    contract_type: str = Field(description="Internal contract type.")

    contract_display: str | None = Field(
        default=None,
        description="Display name.",
    )

    market: str | None = Field(
        default=None,
        description="Market category.",
    )

    submarket: str | None = Field(
        default=None,
        description="Submarket.",
    )

    sentiment: str | None = Field(
        default=None,
        description="Contract sentiment.",
    )

    barrier_category: str | None = Field(
        default=None,
        description="Barrier category.",
    )

    start_type: str | None = Field(
        default=None,
        description="Contract start type.",
    )

    expiry_type: str | None = Field(
        default=None,
        description="Contract expiry type.",
    )

    min_contract_duration: str | None = Field(
        default=None,
        description="Minimum contract duration.",
    )

    max_contract_duration: str | None = Field(
        default=None,
        description="Maximum contract duration.",
    )

    exchange_name: str | None = Field(
        default=None,
        description="Exchange name.",
    )

    underlying_symbol: str | None = Field(
        default=None,
        description="Underlying market symbol.",
    )


class ContractsFor(MarketModel):
    """
    Collection of available contracts returned by the
    contracts_for endpoint.
    """

    available: list[Contract] = Field(
        default_factory=list,
        description="Available contracts.",
    )

    @property
    def count(self) -> int:
        """
        Number of available contracts.
        """
        return len(self.available)
