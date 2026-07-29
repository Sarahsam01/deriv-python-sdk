"""
===========================================================
Deriv SDK

Market Package

Exports all public market interfaces.

Version : 2.3.0
===========================================================
"""

from .exceptions import MarketError
from .models import (
    ActiveSymbol,
    Candle,
    CandleHistory,
    TickHistory,
)
from .service import MarketService

__all__ = [
    "MarketService",
    "MarketError",
    "ActiveSymbol",
    "TickHistory",
    "Candle",
    "CandleHistory",
]