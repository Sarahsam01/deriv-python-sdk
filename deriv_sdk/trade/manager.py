"""
===========================================================
Deriv SDK

Trade Manager

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from deriv_sdk.trade.models import TradeResult


class TradeManager:
    """
    High-level trading workflow.

    Responsibilities
    ----------------
    1. Request proposal
    2. Buy contract
    3. Monitor contract
    4. Return TradeResult
    """

    def __init__(
        self,
        proposal_service,
        buy_service,
        contract_service,
    ) -> None:
        self._proposal = proposal_service
        self._buy = buy_service
        self._contract = contract_service

    async def execute(
        self,
        proposal,
    ) -> TradeResult:
        """
        Execute a complete trade.

        Implementation will be added in the next step.
        """

        raise NotImplementedError