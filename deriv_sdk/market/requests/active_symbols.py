"""
===========================================================
Deriv SDK

Active Symbols Request

Responsibilities
----------------
• Build an active_symbols request
• Validate request parameters

Version : 2.1.0
===========================================================
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ActiveSymbolsRequest(BaseModel):
    """
    Request active trading symbols.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    brief: bool = True

    def to_dict(self) -> dict:
        """
        Convert request to Deriv API payload.
        """

        return {
            "active_symbols": "brief" if self.brief else "full",
        }