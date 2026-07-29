"""
===========================================================
Deriv SDK

Tests - Proposal Builder

Version : 1.0.0
===========================================================
"""

import pytest

from deriv_sdk.proposal_builder.builder import ProposalBuilder
from deriv_sdk.proposal_builder.models import Proposal

# ==========================================================
# Basic Builder
# ==========================================================


def test_build_rise_proposal():

    proposal = ProposalBuilder().symbol("R_100").rise().stake(1).duration(5).build()

    assert isinstance(proposal, Proposal)

    assert proposal.symbol == "R_100"
    assert proposal.contract_type == "CALL"
    assert proposal.amount == 1
    assert proposal.basis == "stake"
    assert proposal.duration == 5
    assert proposal.duration_unit == "t"


def test_build_fall_proposal():

    proposal = ProposalBuilder().symbol("R_100").fall().stake(2).duration(10).build()

    assert proposal.contract_type == "PUT"
    assert proposal.amount == 2


# ==========================================================
# Even / Odd
# ==========================================================


def test_even_contract():

    proposal = ProposalBuilder().symbol("R_100").even().stake(1).duration(1).build()

    assert proposal.contract_type == "DIGITEVEN"


def test_odd_contract():

    proposal = ProposalBuilder().symbol("R_100").odd().stake(1).duration(1).build()

    assert proposal.contract_type == "DIGITODD"


# ==========================================================
# Over / Under
# ==========================================================


def test_digit_over():

    proposal = ProposalBuilder().symbol("R_100").over(6).stake(1).duration(1).build()

    assert proposal.contract_type == "DIGITOVER"
    assert proposal.barrier == "6"


def test_digit_under():

    proposal = ProposalBuilder().symbol("R_100").under(3).stake(1).duration(1).build()

    assert proposal.contract_type == "DIGITUNDER"
    assert proposal.barrier == "3"


# ==========================================================
# Match / Differs
# ==========================================================


def test_digit_match():

    proposal = (
        ProposalBuilder().symbol("R_100").digit_match(7).stake(1).duration(1).build()
    )

    assert proposal.contract_type == "DIGITMATCH"
    assert proposal.prediction == 7


def test_digit_differs():

    proposal = (
        ProposalBuilder().symbol("R_100").digit_differs(2).stake(1).duration(1).build()
    )

    assert proposal.contract_type == "DIGITDIFF"
    assert proposal.prediction == 2


# ==========================================================
# Validation
# ==========================================================


def test_missing_symbol():

    with pytest.raises(ValueError):
        (ProposalBuilder().rise().stake(1).duration(5).build())


def test_missing_amount():

    with pytest.raises(ValueError):
        (ProposalBuilder().symbol("R_100").rise().duration(5).build())


def test_missing_duration():

    with pytest.raises(ValueError):
        (ProposalBuilder().symbol("R_100").rise().stake(1).build())


def test_missing_contract():

    with pytest.raises(ValueError):
        (ProposalBuilder().symbol("R_100").stake(1).duration(5).build())


def test_invalid_prediction():

    with pytest.raises(ValueError):
        (ProposalBuilder().symbol("R_100").digit_match(12).stake(1).duration(5).build())


def test_invalid_barrier():

    with pytest.raises(ValueError):
        (ProposalBuilder().symbol("R_100").over(12).stake(1).duration(5).build())


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict():

    proposal = ProposalBuilder().symbol("R_100").rise().stake(5).duration(10).build()

    payload = proposal.to_dict()

    assert payload["proposal"] == 1
    assert payload["symbol"] == "R_100"
    assert payload["amount"] == 5
    assert payload["contract_type"] == "CALL"


# ==========================================================
# Builder Reset
# ==========================================================


def test_builder_reset():

    builder = ProposalBuilder()

    proposal = builder.symbol("R_100").rise().stake(1).duration(5).build()

    assert proposal.symbol == "R_100"

    with pytest.raises(ValueError):
        builder.build()
