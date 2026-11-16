"""Property-based fuzz tests plus explicit regression cases for all functions."""
import math
import pytest
from hypothesis import given, settings, strategies as st
from scholarship_awards import parse_applicant, marks_average, payable_award

settings.register_profile('lab', max_examples=300, derandomize=True, deadline=None)
settings.load_profile('lab')
inputs = st.one_of(st.text(), st.none(), st.integers(), st.floats(),
                   st.binary(), st.lists(st.integers()), st.dictionaries(st.text(), st.integers()))

@given(inputs)
def test_parse_applicant_no_crash(value):
    result = parse_applicant(value)
    if result is not None:
        category, marks = result
        assert category and math.isfinite(marks) and 0 <= marks <= 100

@given(inputs)
def test_marks_average_no_crash(value):
    result = marks_average(value)
    assert result is None or (math.isfinite(result) and 0 <= result <= 100)

@given(inputs)
def test_payable_award_no_crash(value):
    result = payable_award(value)
    assert result is None or (math.isfinite(result) and result >= 0)

@given(st.sampled_from(['merit', 'need based', 'sports']), st.integers(0, 100))
def test_valid_applicant(category, marks):
    assert parse_applicant(f' {category} : {marks} ') == (category.title(), float(marks))

@given(st.lists(st.integers(0, 100), min_size=1, max_size=100))
def test_average_is_arithmetic_mean(values):
    assert marks_average(','.join(map(str, values))) == pytest.approx(sum(values) / len(values))

@given(st.integers(0, 10**9), st.integers(0, 10**9))
def test_award_formula(award, deduction):
    assert payable_award(f'{award}|{deduction}') == pytest.approx(max(award * 1.18 - deduction, 0))

@pytest.mark.parametrize('value', [None, '', 'merit', ':80', 'merit:NaN', 'merit:inf', 'merit:-1', 'merit:101', 'a:1:2', '123:80'])
def test_invalid_applicant(value):
    assert parse_applicant(value) is None

@pytest.mark.parametrize('value', [None, '', '1,,3', 'one,two', '-1,20', '101', 'NaN', 'inf'])
def test_invalid_marks(value):
    assert marks_average(value) is None

@pytest.mark.parametrize('value', [None, '', '1', '1|2|3', '-1|0', '1|-2', 'NaN|0', 'inf|0', '1.7e308|0'])
def test_invalid_award(value):
    assert payable_award(value) is None

@pytest.mark.parametrize('value,expected', [('1,2', 1.5), ('72,85,90', 247/3), ('1.5,2.5', 2)])
def test_fractional_average_regression(value, expected):
    assert marks_average(value) == pytest.approx(expected)
