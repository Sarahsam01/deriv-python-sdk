"""
===========================================================
Deriv SDK

Transport Messages

Typed request models used by the transport layer.

Version : 0.1.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Message:
    """
    Base transport message.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the message into a dictionary.
        """
        return self.__dict__


@dataclass(slots=True)
class AuthorizeRequest(Message):
    """
    Authorization request.
    """

    token: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorize": self.token,
        }


@dataclass(slots=True)
class ActiveSymbolsRequest(Message):
    """
    Request available symbols.
    """

    active_symbols: str = "brief"

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_symbols": self.active_symbols,
        }


@dataclass(slots=True)
class TickSubscribeRequest(Message):
    """
    Subscribe to live ticks.
    """

    symbol: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticks": self.symbol,
            "subscribe": 1,
        }


@dataclass(slots=True)
class ForgetRequest(Message):
    """
    Cancel a subscription.
    """

    subscription_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "forget": self.subscription_id,
        }


@dataclass(slots=True)
class PingRequest(Message):
    """
    Keep the WebSocket connection alive.
    """

    def to_dict(self) -> dict[str, Any]:
        return {
            "ping": 1,
        }
