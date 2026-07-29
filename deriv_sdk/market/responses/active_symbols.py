"""
===========================================================
Deriv SDK

Active Symbols Response

Responsibilities
----------------
• Parse active_symbols responses
• Convert JSON into strongly typed models

Version : 3.0.0
===========================================================
"""

from __future__ import annotations

from collections.abc import Iterator

from pydantic import BaseModel, ConfigDict, Field

from deriv_sdk.market.models import ActiveSymbol


class ActiveSymbolsResponse(BaseModel):
    """
    Response returned by the active_symbols endpoint.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    active_symbols: list[ActiveSymbol] = Field(
        default_factory=list,
        description="List of active trading symbols.",
    )

    @property
    def count(self) -> int:
        """
        Number of symbols returned.
        """
        return len(self.active_symbols)

    def __len__(self) -> int:
        """
        Number of active symbols.
        """
        return self.count

    def items(self) -> Iterator[ActiveSymbol]:
        """
        Iterate over the active symbols.
        """
        return iter(self.active_symbols)

    def __getitem__(
        self,
        index: int,
    ) -> ActiveSymbol:
        """
        Return an active symbol by index.
        """
        return self.active_symbols[index]
