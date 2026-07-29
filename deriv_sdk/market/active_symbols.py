"""
===========================================================
Deriv SDK

Active Symbols Request

Responsibilities
----------------
• Build an active_symbols request

Version : 0.4.0
===========================================================
"""

from __future__ import annotations


class ActiveSymbolsRequest:
    """
    Build a Deriv active_symbols request.
    """

    def __init__(
        self,
        brief: bool = True,
    ) -> None:
        self.brief = brief

    def to_dict(self) -> dict[str, str]:
        """
        Convert the request into the JSON payload expected
        by the Deriv WebSocket API.
        """

        request: dict[str, str] = {
            "active_symbols": ("brief" if self.brief else "full")
        }

        return request
