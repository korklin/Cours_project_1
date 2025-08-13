import pandas as pd
from datetime import datetime

import pytest

from src.reports import analyze_cards, get_top_transactions, analyze_expenses, analyze_incomes

@pytest.fixture
def sample_df():
    data = {
        "date": pd.to_datetime(["2025-08-01", "2025-08-10", "2025-08-12"]),
        "card_number": ["1111222233334444", "1111222233335555", "1111222233334444"],
        "amount": [-1000.0, 2000.0, -500.0],
        "cashback": [10.0, 20.0, 5.0],
        "category": ["Продукты", "Зарплата", "Наличные"],
        "description": ["Покупка в магазине", "Зарплата", "Снятие наличных"],
        "card_last4": ["4444", "5555", "4444"]
    }
    return pd.DataFrame(data)

def test_analyze_cards(sample_df):
    start = datetime(2025, 8, 1)
    end = datetime(2025, 8, 12)
    result = analyze_cards(sample_df, start, end)
    assert isinstance(result, list)
    assert len(result) == 2
    for card in result:
        assert "card_last4" in card
        assert "total_spent" in card
        assert "cashback" in card

def test_get_top_transactions(sample_df):
    start = datetime(2025, 8, 1)
    end = datetime(2025, 8, 12)
    result = get_top_transactions(sample_df, start, end)
    assert isinstance(result, list)
    assert len(result) <= 5
    assert all("amount" in tx for tx in result)

def test_analyze_expenses(sample_df):
    start = datetime(2025, 8, 1)
    end = datetime(2025, 8, 12)
    result = analyze_expenses(start, end, sample_df)
    assert "total" in result
    assert "main" in result
    assert "cash_and_transfers" in result

def test_analyze_incomes(sample_df):
    start = datetime(2025, 8, 1)
    end = datetime(2025, 8, 12)
    result = analyze_incomes(start, end, sample_df)
    assert "total" in result
    assert "main" in result
