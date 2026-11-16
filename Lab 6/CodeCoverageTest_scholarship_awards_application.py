"""Simple tests covering every executable line in the application."""

import pytest
from scholarship_awards import award_amount, is_eligible, application_status


def test_invalid_inputs():
    with pytest.raises(ValueError, match="unknown category"):
        award_amount("music", 80, "low", False)
    with pytest.raises(ValueError, match="invalid marks"):
        award_amount("merit", -1, "low", False)


def test_award_amount():
    assert award_amount("merit", 70, "low", False) == 0
    assert award_amount("merit", 90, "low", True) == 3200
    assert award_amount("arts", 70, "high", False) == 300


def test_eligibility():
    assert is_eligible(50, 2, True) is True
    assert is_eligible(74, 0, False) is False
    assert is_eligible(90, 0, False) is True


def test_application_status():
    assert application_status(40, True, True) == "open"
    assert application_status(10, False, False) == "closing"
    assert application_status(4, False, False) == "closed"
