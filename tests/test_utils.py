import pytest
from datetime import datetime
from src.utils import parse_date, get_date_range, get_greeting

def test_parse_date():
    assert parse_date("2025-08-12 14:30:00") == datetime(2025, 8, 12, 14, 30, 0)

def test_get_date_range_month():
    date = datetime(2025, 8, 12)
    start, end = get_date_range(date, "M")
    assert start == datetime(2025, 8, 1)
    assert end == date

def test_get_date_range_week():
    date = datetime(2025, 8, 7)  # Четверг
    start, end = get_date_range(date, "W")
    assert start == datetime(2025, 8, 4)  # Понедельник
    assert end == date

def test_get_greeting():
    assert get_greeting(datetime(2025, 8, 12, 8, 0, 0)) == "Доброе утро"
    assert get_greeting(datetime(2025, 8, 12, 13, 0, 0)) == "Добрый день"
    assert get_greeting(datetime(2025, 8, 12, 19, 0, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2025, 8, 12, 3, 0, 0)) == "Доброй ночи"