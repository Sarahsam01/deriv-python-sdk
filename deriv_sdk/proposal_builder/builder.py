"""
===========================================================
Deriv SDK

Proposal Builder

Responsibilities
----------------
• Fluent proposal builder
• Validate proposal fields
• Produce Proposal models

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from .models import Proposal


class ProposalBuilder:
    """
    Fluent builder for Deriv proposal requests.
    """

    def __init__(self) -> None:
        self.reset()

    # =====================================================
    # Internal
    # =====================================================

    def reset(self) -> ProposalBuilder:
        """
        Reset the builder.
        """

        self._amount: float | None = None
        self._basis = "stake"
        self._contract_type: str | None = None
        self._currency = "USD"
        self._duration: int | None = None
        self._duration_unit = "t"
        self._symbol: str | None = None
        self._barrier: str | None = None
        self._prediction: int | None = None

        return self

    # =====================================================
    # Market
    # =====================================================

    def symbol(self, symbol: str) -> ProposalBuilder:
        self._symbol = symbol
        return self

    def currency(self, currency: str) -> ProposalBuilder:
        self._currency = currency
        return self

    # =====================================================
    # Money
    # =====================================================

    def stake(self, amount: float) -> ProposalBuilder:
        self._amount = amount
        self._basis = "stake"
        return self

    def payout(self, amount: float) -> ProposalBuilder:
        self._amount = amount
        self._basis = "payout"
        return self

    # =====================================================
    # Duration
    # =====================================================

    def duration(
        self,
        duration: int,
        unit: str = "t",
    ) -> ProposalBuilder:
        self._duration = duration
        self._duration_unit = unit
        return self

    # =====================================================
    # Contract Types
    # =====================================================

    def rise(self) -> ProposalBuilder:
        self._contract_type = "CALL"
        return self

    def fall(self) -> ProposalBuilder:
        self._contract_type = "PUT"
        return self

    def higher(self) -> ProposalBuilder:
        self._contract_type = "CALL"
        return self

    def lower(self) -> ProposalBuilder:
        self._contract_type = "PUT"
        return self

    def even(self) -> ProposalBuilder:
        self._contract_type = "DIGITEVEN"
        return self

    def odd(self) -> ProposalBuilder:
        self._contract_type = "DIGITODD"
        return self

    def over(self, barrier: int) -> ProposalBuilder:
        self._contract_type = "DIGITOVER"
        self._barrier = str(barrier)
        return self

    def under(self, barrier: int) -> ProposalBuilder:
        self._contract_type = "DIGITUNDER"
        self._barrier = str(barrier)
        return self

    def digit_match(self, prediction: int) -> ProposalBuilder:
        self._contract_type = "DIGITMATCH"
        self._prediction = prediction
        return self

    def digit_differs(self, prediction: int) -> ProposalBuilder:
        self._contract_type = "DIGITDIFF"
        self._prediction = prediction
        return self

    # =====================================================
    # Validation
    # =====================================================

    def _validate(self) -> None:
        if self._symbol is None:
            raise ValueError("Symbol is required.")

        if self._amount is None:
            raise ValueError("Amount is required.")

        if self._contract_type is None:
            raise ValueError("Contract type is required.")

        if self._duration is None:
            raise ValueError("Duration is required.")

        if self._prediction is not None and not 0 <= self._prediction <= 9:
            raise ValueError("Prediction must be between 0 and 9.")

        if self._barrier is not None:
            barrier = int(self._barrier)
            if not 0 <= barrier <= 9:
                raise ValueError("Barrier must be between 0 and 9.")

    def _required_fields(self) -> tuple[float, str, int, str]:
        """
        Return validated non-optional fields.

        This helper narrows the optional builder state into concrete
        values for static type checkers.
        """
        self._validate()

        assert self._amount is not None
        assert self._contract_type is not None
        assert self._duration is not None
        assert self._symbol is not None

        return (
            self._amount,
            self._contract_type,
            self._duration,
            self._symbol,
        )

    # =====================================================
    # Build
    # =====================================================

    def build(self) -> Proposal:
        """
        Build a validated Proposal model.
        """

        amount, contract_type, duration, symbol = self._required_fields()

        proposal = Proposal(
            amount=amount,
            basis=self._basis,
            contract_type=contract_type,
            currency=self._currency,
            duration=duration,
            duration_unit=self._duration_unit,
            symbol=symbol,
            barrier=self._barrier,
            prediction=self._prediction,
        )

        self.reset()

        return proposal
