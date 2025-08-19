import json
from typing import Hashable, Iterator

import pandas as pd
import pytest
from pandas import Series

from src.views import get_events_page, get_main_page


def test_get_main_page_returns_str() -> None:
    result = get_main_page()
    assert isinstance(result, str)


def test_get_main_page_json_structure() -> None:
    result = get_main_page()
    data = json.loads(result)

    # Проверяем, что это словарь
    assert isinstance(data, dict)

    # Проверяем наличие ключей
    assert "приветствие" in data
    assert "валюты" in data
    assert "акции" in data
    assert "карты" in data
    assert "топ транзакции" in data


# === Параметризация ===
@pytest.mark.parametrize(
    "datetime_str, expected_greeting",
    [
        ("2021-12-21 06:30:00", "Доброе утро"),
        ("2021-12-21 13:00:00", "Добрый день"),
        ("2021-12-21 19:30:00", "Добрый вечер"),
        ("2021-12-21 02:00:00", "Доброй ночи"),
    ],
)
def test_get_main_page_greeting(datetime_str: str, expected_greeting: str) -> None:
    result = get_main_page(datetime_str)
    data = json.loads(result)
    assert data["приветствие"].startswith(expected_greeting)


# === Моки для API ===
def test_get_main_page_with_mocked_currency_and_stocks(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_currency = [
        {"валюта": "USD", "курс": 75.0},
        {"валюта": "EUR", "курс": 90.0},
    ]
    mock_stocks = [
        {"тикер": "AAPL", "цена": 180.0},
        {"тикер": "TSLA", "цена": 700.0},
    ]

    monkeypatch.setattr("src.views.get_currency_rates", lambda *a, **kw: mock_currency)
    monkeypatch.setattr("src.views.get_stock_prices", lambda *a, **kw: mock_stocks)

    result = get_main_page("2021-12-21 10:00:00")
    assert isinstance(result, str)

    data = json.loads(result)
    assert data["валюты"]["USD"] == 75.0
    assert data["валюты"]["EUR"] == 90.0
    assert data["акции"]["AAPL"] == 180.0


def test_get_events_page_returns_dict() -> None:
    class DummyDF(pd.DataFrame):
        def iterrows(self) -> Iterator[tuple[Hashable, Series]]:
            yield 0, Series(
                {
                    "Дата операции": "2021-12-21 10:00:00",
                    "Сумма операции": 100,
                    "Категория": "Тест",
                    "Описание": "Dummy event",
                }
            )

    dummy_df = DummyDF()
    result = get_events_page(dummy_df)

    # проверяем, что вернулся dict с ключом "events"
    assert isinstance(result, dict)
    assert "events" in result
    assert isinstance(result["events"], list)
    assert result["events"][0]["описание"] == "Test Event"
    assert result["events"][0]["категория"] == "Тестовая категория"
    assert result["events"][0]["сумма"] == 123.45
    assert result["events"][0]["дата"] == "21.12.2021 10:00:00"
