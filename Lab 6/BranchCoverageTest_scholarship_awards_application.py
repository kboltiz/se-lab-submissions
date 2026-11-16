"""Cover both outcomes of decisions and important boundary values."""

import pytest
from scholarship_awards import award_amount, is_eligible, application_status


def test_invalid_inputs():
    with pytest.raises(ValueError, match="unknown category"):
        award_amount("music", 80, "low", False)
    with pytest.raises(ValueError, match="invalid marks"):
        award_amount("merit", -1, "low", False)


def test_award_cutoffs_and_renewals():
    assert award_amount("merit", 0, "low", False) == 0
    assert award_amount("merit", 75, "low", False) == 0
    assert award_amount("merit", 76, "low", False) == 100
    assert award_amount("merit", 75, "low", True) == 500
    assert award_amount("sports", 60, "low", True) == 0
    assert award_amount("sports", 61, "low", True) == 100
    assert award_amount("arts", 65, "high", False) == 0
    assert award_amount("arts", 65, "high", True) == 300


def test_award_rates():
    assert award_amount("merit", 90, "low", False) == 1500
    assert award_amount("merit", 91, "low", False) == 2560
    assert award_amount("merit", 90, "high", False) == 900
    assert award_amount("merit", 91, "high", False) == 1600


def test_eligibility():
    assert is_eligible(50, 2, True) is True
    assert is_eligible(90, 3, True) is False
    assert is_eligible(74, 0, False) is False
    assert is_eligible(75, 1, False) is True
    assert is_eligible(75, 2, False) is False


@pytest.mark.parametrize("renewal,paper,cutoff", [
    (False, False, 20),
    (False, True, 30),
    (True, False, 30),
    (True, True, 40),
])
def test_application_status_boundaries(renewal, paper, cutoff):
    assert application_status(cutoff, renewal, paper) == "open"
    assert application_status(cutoff - 1, renewal, paper) == "closing"
    assert application_status(cutoff - 15, renewal, paper) == "closing"
    assert application_status(cutoff - 16, renewal, paper) == "closed"
