"""
===========================================================
Deriv SDK

Proposal Service

Responsibilities
----------------
• Validate proposal requests
• Build proposal payloads
• Request trade quotations
• Support ProposalBuilder
• Parse proposal responses
• Return Proposal models

Version : 8.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.models.proposal import Proposal
from deriv_sdk.proposal_builder.models import Proposal as ProposalRequest
from deriv_sdk.trading.base_service import BaseTradingService
from deriv_sdk.transport.websocket import WebSocketClient


class ProposalService(BaseTradingService[Proposal]):
    """
    Service responsible for requesting contract proposals
    from the Deriv API.
    """

    def __init__(
        self,
        websocket: WebSocketClient,
    ) -> None:
        super().__init__(websocket)

    # =====================================================
    # Standard API
    # =====================================================

    async def request(
        self,
        *,
        symbol: str,
        contract_type: str,
        amount: float,
        basis: str = "stake",
        currency: str = "USD",
        duration: int = 1,
        duration_unit: str = "t",
        barrier: str | None = None,
    ) -> Proposal:
        """
        Request a proposal from individual parameters.
        """

        self._validate_request(
            symbol=symbol,
            contract_type=contract_type,
            amount=amount,
            basis=basis,
            currency=currency,
            duration=duration,
            duration_unit=duration_unit,
        )

        payload = self._build_request(
            symbol=symbol,
            contract_type=contract_type,
            amount=amount,
            basis=basis,
            currency=currency,
            duration=duration,
            duration_unit=duration_unit,
            barrier=barrier,
        )

        return await self._execute(
            payload=payload,
            expected="proposal",
        )

    # =====================================================
    # Proposal Builder API
    # =====================================================

    async def quote(
        self,
        proposal: ProposalRequest,
    ) -> Proposal:
        """
        Request a proposal using a ProposalBuilder model.

        Example
        -------
        proposal = (
            ProposalBuilder()
            .symbol("R_100")
            .rise()
            .stake(1)
            .duration(5)
            .build()
        )

        quote = await service.quote(proposal)
        """

        return await self._execute(
            payload=proposal.to_dict(),
            expected="proposal",
        )

    # =====================================================
    # Validation
    # =====================================================

    def _validate_request(
        self,
        *,
        symbol: str,
        contract_type: str,
        amount: float,
        basis: str,
        currency: str,
        duration: int,
        duration_unit: str,
    ) -> None:
        """
        Validate proposal request parameters.
        """

        if not symbol.strip():
            raise ValueError("symbol is required.")

        if not contract_type.strip():
            raise ValueError("contract_type is required.")

        if amount <= 0:
            raise ValueError("amount must be greater than zero.")

        if basis not in {"stake", "payout"}:
            raise ValueError("basis must be 'stake' or 'payout'.")

        if not currency.strip():
            raise ValueError("currency is required.")

        if duration <= 0:
            raise ValueError("duration must be greater than zero.")

        if duration_unit not in {
            "t",
            "s",
            "m",
            "h",
            "d",
        }:
            raise ValueError("Invalid duration_unit.")

    # =====================================================
    # Payload Builder
    # =====================================================

    def _build_request(
        self,
        *,
        symbol: str,
        contract_type: str,
        amount: float,
        basis: str,
        currency: str,
        duration: int,
        duration_unit: str,
        barrier: str | None,
    ) -> dict[str, object]:
        """
        Build a proposal request payload.
        """

        payload: dict[str, object] = {
            "proposal": 1,
            "symbol": symbol,
            "contract_type": contract_type,
            "amount": amount,
            "basis": basis,
            "currency": currency,
            "duration": duration,
            "duration_unit": duration_unit,
        }

        if barrier is not None:
            payload["barrier"] = barrier

        return payload

    # =====================================================
    # Response Parsing
    # =====================================================

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> Proposal:
        """
        Convert the API response into a Proposal model.
        """

        return Proposal.from_api(response)
