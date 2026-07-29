"""
===========================================================
Deriv SDK

Market Package

Exports all public market interfaces.

Version : 2.4.0
===========================================================
"""

from .exceptions import MarketError
from .models import (
    ActiveSymbol,
    Candle,
    CandleHistory,
    TickHistory,
)
from .responses import TicksHistoryResponse
from .service import MarketService

__all__ = [
    "MarketService",
    "MarketError",
    "ActiveSymbol",
    "TickHistory",
    "Candle",
    "CandleHistory",
    "TicksHistoryResponse",
]
