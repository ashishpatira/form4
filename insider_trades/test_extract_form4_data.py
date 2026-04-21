import sys
from unittest.mock import MagicMock

# Mock missing dependencies before importing the module under test
sys.modules["requests"] = MagicMock()
sys.modules["ratelimit"] = MagicMock()

import pytest
from datetime import date
from form4_insider_trades.extract_form4_data import get_quarter

@pytest.mark.parametrize("input_date, expected_quarter", [
    (date(2023, 1, 1), 1),
    (date(2023, 2, 15), 1),
    (date(2023, 3, 31), 1),
    (date(2023, 4, 1), 2),
    (date(2023, 5, 20), 2),
    (date(2023, 6, 30), 2),
    (date(2023, 7, 1), 3),
    (date(2023, 8, 10), 3),
    (date(2023, 9, 30), 3),
    (date(2023, 10, 1), 4),
    (date(2023, 11, 25), 4),
    (date(2023, 12, 31), 4),
])
def test_get_quarter(input_date, expected_quarter):
    assert get_quarter(input_date) == expected_quarter

def test_get_quarter_leap_year():
    # Leap year check
    assert get_quarter(date(2024, 2, 29)) == 1

@pytest.mark.parametrize("month, expected_quarter", [
    (1, 1), (2, 1), (3, 1),
    (4, 2), (5, 2), (6, 2),
    (7, 3), (8, 3), (9, 3),
    (10, 4), (11, 4), (12, 4),
])
def test_get_quarter_all_months(month, expected_quarter):
    assert get_quarter(date(2023, month, 1)) == expected_quarter
