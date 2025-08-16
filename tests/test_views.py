import pytest
import pandas as pd
from datetime import datetime
from src import views


def test_parse_date():
    """Тест: проверка корректного парсинга строки в datetime."""
    assert views.parse_date("2021-12-21 10:00:00") == datetime(2021, 12, 21, 10, 0, 0)


def test_get_date_range_week():
    """Тест: диапазон недели начинается с понедельника и заканчивается текущим днём."""
    d = datetime(2021, 12, 21)  # вторник
    start, end = views.get_date_range(d, "W")
    assert start.weekday() == 0
    assert end == d


def test_get_date_range_invalid():
    """Тест: при некорректном типе диапазона выбрасывается ошибка."""
    with pytest.raises(ValueError):
        views.get_date_range(datetime.now(), "BAD")


@pytest.mark.parametrize("hour,expected", [
    (6, "Доброе утро"),
    (13, "Добрый день"),
    (18, "Добрый вечер"),
    (2, "Доброй ночи"),
])
def test_get_greeting(hour, expected):
    """Тест: приветствие соответствует времени суток."""
    d = datetime(2021, 12, 21, hour, 0)
    assert views.get_greeting(d) == expected


def test_analyze_cards_and_top_transactions():
    """Тест: корректный расчёт трат по картам и выборка топовых транзакций."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["2021-12-01", "2021-12-05"]),
        "amount": [100, 200],
        "cashback": [1, 2],
        "category": ["A", "B"],
        "description": ["desc1", "desc2"],
        "card_last4": ["1111", "1111"]
    })
    cards = views.analyze_cards(df, datetime(2021, 12, 1), datetime(2021, 12, 31))
    assert cards[0]["total_spent"] == 300
    top = views.get_top_transactions(df, datetime(2021, 12, 1), datetime(2021, 12, 31))
    assert top[0]["amount"] == 200


def test_get_currency_rates_mock(monkeypatch):
    """Тест: замоканный ответ API валют возвращает курсы в виде словаря."""
    def fake_get(url, params, headers, timeout):
        class R:
            def raise_for_status(self): pass
            def json(self): return {"rates": {"USD": 74.12, "EUR": 86.53}}
        return R()
    monkeypatch.setattr(views.requests, "get", fake_get)
    rates = views.get_currency_rates(["USD", "EUR"], base="RUB", access_key="fake")
    assert "USD" in rates and isinstance(rates["USD"], float)


def test_get_stock_prices_mock(monkeypatch):
    """Тест: замоканный ответ API акций возвращает корректную цену."""
    def fake_get(url, params, timeout):
        class R:
            def raise_for_status(self): pass
            def json(self): return {"Global Quote": {"05. price": "123.45"}}
        return R()
    monkeypatch.setattr(views.requests, "get", fake_get)
    prices = views.get_stock_prices(["AAPL"], "fake")
    assert prices["AAPL"] == 123.45
