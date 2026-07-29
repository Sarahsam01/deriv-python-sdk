"""
===========================================================
Deriv SDK

Trade Manager

Coordinates the complete trading workflow.

Responsibilities
----------------
1. Request a proposal
2. Buy a contract
3. Monitor the contract
4. Return a TradeResult

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from typing import Protocol

from deriv_sdk.proposal_builder.models import Proposal
from deriv_sdk.trade.models import TradeResult


class ProposalServiceProtocol(Protocol):
    """
    Interface for the proposal service.
    """

    async def request(self, proposal: Proposal) -> object: ...


class BuyServiceProtocol(Protocol):
    """
    Interface for the buy service.
    """

    async def buy(self, proposal: object) -> object: ...


class ContractServiceProtocol(Protocol):
    """
    Interface for the contract monitoring service.
    """

    async def monitor(self, contract_id: int | str) -> TradeResult: ...


class TradeManager:
    """
    High-level trading workflow.
    """

    def __init__(
        self,
        proposal_service: ProposalServiceProtocol,
        buy_service: BuyServiceProtocol,
        contract_service: ContractServiceProtocol,
    ) -> None:
        self._proposal = proposal_service
        self._buy = buy_service
        self._contract = contract_service

    async def execute(
        self,
        proposal: Proposal,
    ) -> TradeResult:
        """
        Execute a complete trade.

        This workflow will be implemented in a later version.
        """
        raise NotImplementedError("Trade execution is not yet implemented.")
