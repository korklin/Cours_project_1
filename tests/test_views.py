from src.views import get_main_page, get_events_page


def test_get_main_page(monkeypatch):
    monkeypatch.setattr("src.views.get_currency_rates", lambda x: {c: 100.0 for c in x})
    monkeypatch.setattr("src.views.get_stock_prices", lambda x: {s: 200.0 for s in x})
    monkeypatch.setattr("src.views.load_operations", lambda: __import__('pandas').DataFrame(columns=[
        "date", "card_number", "amount", "cashback", "category", "description", "card_last4"
    ]))

    result = get_main_page("2025-08-12 14:30:00")
    assert "greeting" in result
    assert "cards" in result
    assert "currencies" in result
    assert "stocks" in result


def test_get_events_page(monkeypatch):
    monkeypatch.setattr("src.views.get_currency_rates", lambda x: {c: 100.0 for c in x})
    monkeypatch.setattr("src.views.get_stock_prices", lambda x: {s: 200.0 for s in x})
    monkeypatch.setattr("src.views.load_operations", lambda: __import__('pandas').DataFrame(columns=[
        "date", "card_number", "amount", "cashback", "category", "description", "card_last4"
    ]))

    result = get_events_page("2025-08-12 14:30:00", "M")
    assert "expenses" in result
    assert "incomes" in result
