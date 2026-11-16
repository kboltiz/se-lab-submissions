"""Scholarship input validation. Invalid inputs return None, without raising."""
import math


def _number(text, maximum=None):
    value = float(text)
    if not math.isfinite(value) or value < 0:
        raise ValueError('Expected a finite non-negative number')
    if maximum is not None and value > maximum:
        raise ValueError('Marks must be between 0 and 100')
    return value


def parse_applicant(text):
    """Return (category, marks), or None for malformed or out-of-range input."""
    if not isinstance(text, str):
        return None
    try:
        category, marks = text.split(':')
        category = category.strip()
        if not category or not all(c.isalpha() or c.isspace() for c in category):
            return None
        return category.title(), _number(marks, 100)
    except (ValueError, OverflowError):
        return None


def marks_average(marks_csv):
    """Return the arithmetic mean of CSV marks in [0, 100], or None."""
    if not isinstance(marks_csv, str):
        return None
    try:
        values = [_number(token, 100) for token in marks_csv.split(',')]
        return sum(values) / len(values)
    except (ValueError, OverflowError):
        return None


def payable_award(text):
    """Return max(award * 1.18 - deduction, 0), or None for invalid input."""
    if not isinstance(text, str):
        return None
    try:
        award, deduction = text.split('|')
        total = _number(award) * 1.18 - _number(deduction)
        return max(total, 0.0) if math.isfinite(total) else None
    except (ValueError, OverflowError):
        return None


def main():
    for heading, prompt, function in [
        ('parse_applicant', 'Enter category:marks (e.g. merit:82): ', parse_applicant),
        ('marks_average', 'Enter marks as CSV (e.g. 72,85,90): ', marks_average),
        ('payable_award', 'Enter award|deduction (e.g. 5000|500): ', payable_award),
    ]:
        print('==== Running ' + heading + ' ====')
        try:
            result = function(input(prompt))
        except EOFError:
            print('Input ended.')
            return
        print('Invalid input.' if result is None else 'Result: ' + str(result))


if __name__ == '__main__':
    main()
