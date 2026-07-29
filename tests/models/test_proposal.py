import pytest

from deriv_sdk.models.proposal import Proposal


def sample_response():
    return {
        "proposal": {
            "id": "12345",
            "ask_price": 1.25,
            "payout": 2.35,
            "spot": 1234.5,
            "display_value": 1.25,
            "currency": "USD",
            "contract_type": "CALL",
            "symbol": "R_100",
            "duration": 5,
            "duration_unit": "t",
            "longcode": "Sample proposal",
        }
    }


def test_proposal_from_api():
    proposal = Proposal.from_api(sample_response())

    assert proposal.id == "12345"
    assert proposal.currency == "USD"
    assert proposal.symbol == "R_100"
    assert proposal.duration == 5


def test_proposal_to_dict():
    proposal = Proposal.from_api(sample_response())

    data = proposal.to_dict()

    assert data["id"] == "12345"
    assert data["currency"] == "USD"
    assert data["symbol"] == "R_100"


def test_proposal_raw_response():
    proposal = Proposal.from_api(sample_response())

    assert proposal.raw == sample_response()


def test_missing_proposal_key():
    with pytest.raises(KeyError):
        Proposal.from_api({})
