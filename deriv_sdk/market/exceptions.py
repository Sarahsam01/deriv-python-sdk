"""
===========================================================
Deriv SDK

Market Exceptions

Version : 1.0.0
===========================================================
"""


class MarketError(Exception):
    """
    Base exception for all market-related errors.
    """


class InvalidSymbolError(MarketError):
    """
    Raised when an invalid market symbol is supplied.
    """


class SubscriptionError(MarketError):
    """
    Raised when a market subscription fails.
    """


class TickHistoryError(MarketError):
    """
    Raised when tick history retrieval fails.
    """


class ContractsError(MarketError):
    """
    Raised when contract retrieval fails.
    """


__all__ = [
    "ContractsError",
    "InvalidSymbolError",
    "MarketError",
    "SubscriptionError",
    "TickHistoryError",
]
