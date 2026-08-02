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
    product_type: str | None = "basic"
    landing_company_short: str | None = None

    def to_dict(self) -> dict:
        """
        Convert request to Deriv API payload.
        """

        payload = {
            "active_symbols": "brief" if self.brief else "full",
        }
        if self.product_type is not None:
            payload["product_type"] = self.product_type
        if self.landing_company_short is not None:
            payload["landing_company_short"] = self.landing_company_short
        return payload
