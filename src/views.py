import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import requests

from src.settings import (BASE_CURRENCY, CURRENCY_API_KEY,
                          STOCK_API_KEY, USER_CURRENCIES, USER_STOCKS)
from src.utils import prepare_events

logger = logging.getLogger(__name__)


def get_currency_rates(
    currencies: list[str], base: str = "RUB", access_key: str | None = None
) -> list[dict]:
    """
    Получение курсов валют.
    Если есть access_key → используем apilayer.
    Иначе используем exchangerate.host.
    """
    try:
        if access_key:
            # apilayer
            url = "https://api.apilayer.com/exchangerates_data/latest"
            params = {"base": base, "symbols": ",".join(currencies)}
            headers = {"apikey": access_key}
        else:
            # exchangerate.host
            url = "https://api.exchangerate.host/latest"
            params = {"base": base, "symbols": ",".join(currencies)}
            headers = {}

        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        rates = []
        for curr in currencies:
            rate = data.get("rates", {}).get(curr)
            if rate:
                rates.append({"валюта": curr, "курс": rate})

        return rates

    except requests.exceptions.Timeout:
        logger.error("⏳ Ошибка: API не ответило по таймауту")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"⚠ Ошибка при получении курсов валют: {e}")
        return []


def get_stock_prices(stocks: list[str], api_key: str | None = None) -> list[dict]:
    """
    Получение цен акций.
    Если есть api_key → используем Alpha Vantage.
    Иначе возвращаем 0.
    """
    prices = []
    for ticker in stocks:
        try:
            if not api_key:
                prices.append({"тикер": ticker, "цена": 0.0})
                continue

            url = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": api_key}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            price = float(data.get("Global Quote", {}).get("05. price", 0.0))
            prices.append({"тикер": ticker, "цена": price})
        except Exception as e:
            logger.error(f"⚠ Ошибка при получении акции {ticker}: {e}")
            prices.append({"тикер": ticker, "цена": 0.0})

    return prices


def get_main_page(datetime_str: Optional[str] = None) -> str:
    """
    Главная страница: приветствие, карты, топ транзакции, валюты и акции.
    """
    if datetime_str is None:
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Приветствие
    hour = int(datetime_str.split(" ")[1].split(":")[0])
    if 5 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    # Карты — пока тестовые данные
    cards = [
        {"карта": "4556", "потрачено": 2547.10, "кэшбэк": 25.47},
        {"карта": "5091", "потрачено": -9405.13, "кэшбэк": -94.05},
        {"карта": "7197", "потрачено": -13995.30, "кэшбэк": -139.95},
        {"карта": "nan", "потрачено": -20246.56, "кэшбэк": -202.47},
    ]

    # Топ транзакции — пока тестовые данные
    top_transactions = [
        {
            "дата": "05.12.2021",
            "сумма": 3500.0,
            "категория": "Пополнения",
            "описание": "Внесение наличных через банкомат Тинькофф",
        },
        {
            "дата": "12.12.2021",
            "сумма": 1721.38,
            "категория": "Каршеринг",
            "описание": "Ситидрайв",
        },
        {
            "дата": "20.12.2021",
            "сумма": 495.0,
            "категория": "Бонусы",
            "описание": "Выплата по вашему обращению",
        },
        {
            "дата": "16.12.2021",
            "сумма": 453.0,
            "категория": "Бонусы",
            "описание": "Кэшбэк за обычные покупки",
        },
        {
            "дата": "20.12.2021",
            "сумма": 421.0,
            "категория": "Различные товары",
            "описание": "Ozon.ru",
        },
    ]

    # Курсы валют
    currency_rates = get_currency_rates(
        USER_CURRENCIES, base=BASE_CURRENCY, access_key=CURRENCY_API_KEY
    )

    # Акции
    stocks = get_stock_prices(USER_STOCKS, api_key=STOCK_API_KEY)

    data: Dict[str, Any] = {
        "приветствие": f"{greeting}! Сейчас {datetime_str}",
        "валюты": {item["валюта"]: item["курс"] for item in currency_rates},
        "акции": {item["тикер"]: item["цена"] for item in stocks},
        "карты": cards,
        "топ транзакции": top_transactions,
    }
    logger.info("Обработка страницы 'Главная'")

    return json.dumps(data, ensure_ascii=False)


def get_events_page(df: pd.DataFrame) -> dict:
    """
    Страница событий: принимает DataFrame и возвращает JSON-словарь.
    """
    events = prepare_events(df)
    return {"events": events}
