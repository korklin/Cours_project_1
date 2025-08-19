import json

import pandas as pd

from src.views import get_events_page, get_main_page


def test_get_main_page_returns_str():
    result = get_main_page()
    assert isinstance(result, str)


def test_get_main_page_json_structure():
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

def test_get_main_page_greeting_contains_time():
    result = get_main_page("2021-12-21 10:00:00")
    data = json.loads(result)

    greeting = data["приветствие"]
    assert "Доброе утро" in greeting or "Добрый день" in greeting or "Добрый вечер" in greeting or "Доброй ночи" in greeting
    assert "2021-12-21 10:00:00" in greeting

def test_get_main_page_currency_and_stocks():
    result = get_main_page()
    data = json.loads(result)

    assert isinstance(data["валюты"], dict)
    assert isinstance(data["акции"], dict)

    for currency in ["USD", "EUR", "CNY"]:
        assert currency in data["валюты"]

    for stock in ["AAPL", "TSLA", "GOOGL"]:
        assert stock in data["акции"]

def test_get_events_page_returns_json_dict():
    df = pd.DataFrame(
        [
            {
                "Дата операции": "2021-12-21 10:00:00",
                "Сумма операции": -100,
                "Категория": "Еда",
                "Описание": "Обед",
            }
        ]
    )

    result = get_events_page(df)
    assert isinstance(result, dict)
    assert "events" in result
    assert len(result["events"]) > 0
