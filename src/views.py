import json
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_date(date_str: str) -> datetime:
    """Преобразует строку в объект datetime.

    Args:
        date_str (str): Дата в формате "%Y-%m-%d %H:%M:%S".

    Returns:
        datetime: Объект даты и времени.
    """
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def get_date_range(date: datetime, range_type: str) -> Tuple[datetime, datetime]:
    """Возвращает начало и конец периода в зависимости от типа диапазона.

    Args:
        date (datetime): Опорная дата.
        range_type (str): Тип диапазона:
            - "W" (неделя),
            - "M" (месяц),
            - "Y" (год),
            - "ALL" (с 2000 года).

    Returns:
        (datetime, datetime): Начало и конец периода.

    Raises:
        ValueError: Если указан неверный тип диапазона.
    """
    if range_type == "W":
        start = date - timedelta(days=date.weekday())
    elif range_type == "M":
        start = date.replace(day=1)
    elif range_type == "Y":
        start = date.replace(month=1, day=1)
    elif range_type == "ALL":
        start = datetime(2000, 1, 1)
    else:
        raise ValueError("Invalid range_type")
    end = date
    return start, end


def get_greeting(date: datetime) -> str:
    """Формирует приветствие в зависимости от времени суток.

    Args:
        date (datetime): Дата и время.

    Returns:
        str: Приветствие (на русском).
    """
    hour = date.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def load_operations() -> pd.DataFrame:
    """Загружает операции из Excel и приводит их к стандартному виду.

    Returns:
        pd.DataFrame: Таблица с колонками:
            - date,
            - card_number,
            - amount,
            - cashback,
            - category,
            - description,
            - card_last4.
    """
    path = os.path.join(BASE_DIR, "data", "operations.xlsx")
    df = pd.read_excel(path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df.rename(columns={
        "Дата операции": "date",
        "Номер карты": "card_number",
        "Сумма операции": "amount",
        "Кэшбэк": "cashback",
        "Категория": "category",
        "Описание": "description"
    }, inplace=True)
    df["amount"] = df["amount"].astype(float)
    df["cashback"] = df["cashback"].astype(float)
    df["card_last4"] = df["card_number"].astype(str).str[-4:]
    return df


def analyze_cards(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Считает траты и кешбэк по каждой карте за период.

    Args:
        df (pd.DataFrame): Таблица операций.
        start_date (datetime): Начало периода.
        end_date (datetime): Конец периода.

    Returns:
        list[dict]: Список словарей с итогами по картам.
    """
    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    cards = []
    for card, sub in df_range.groupby("card_last4"):
        total = sub["amount"].sum()
        cashback = round(total * 0.01, 2)
        cards.append({
            "last_digits": card,
            "total_spent": round(total, 2),
            "cashback": cashback
        })
    return cards


def get_top_transactions(df: pd.DataFrame, start_date: datetime, end_date: datetime, n: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-N операций по сумме.

    Args:
        df (pd.DataFrame): Таблица операций.
        start_date (datetime): Начало периода.
        end_date (datetime): Конец периода.
        n (int): Количество операций.

    Returns:
        list[dict]: Список словарей с данными о транзакциях.
    """
    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    top = df_range.nlargest(n, "amount")
    return [
        {
            "date": row["date"].strftime("%d.%m.%Y"),
            "amount": round(row["amount"], 2),
            "category": row["category"],
            "description": row["description"]
        }
        for _, row in top.iterrows()
    ]


def get_currency_rates(currencies: List[str], base: str = "RUB", access_key: Optional[str] = None) -> Dict[str, float]:
    """Получает курсы валют с помощью API Apilayer.

    Args:
        currencies (list[str]): Целевые валюты.
        base (str): Базовая валюта.
        access_key (str, optional): API-ключ Apilayer.

    Returns:
        dict: Словарь {валюта: курс}.
    """
    url = "https://api.apilayer.com/exchangerates_data/latest"
    params = {
        "symbols": ",".join(currencies),
        "base": base
    }
    headers = {"apikey": access_key} if access_key else {}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise ValueError(f"Currency API error: {data['error']}")

    rates = data.get("rates")
    if not rates:
        raise ValueError("Unexpected response: no rates")

    return {cur: round(float(rates.get(cur, 0.0)), 4) for cur in currencies}


def get_stock_prices(tickers: List[str], api_key: str) -> Dict[str, float]:
    """Получает цены акций с AlphaVantage.

    Args:
        tickers (list[str]): Тикеры акций.
        api_key (str): API-ключ AlphaVantage.

    Returns:
        dict: Словарь {тикер: цена}.
    """
    base_url = "https://www.alphavantage.co/query"
    prices: Dict[str, float] = {}
    for ticker in tickers:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key
        }
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            price = float(data["Global Quote"]["05. price"])
        except Exception:
            price = 0.0
        prices[ticker] = round(price, 2)
    return prices


def get_user_settings(path: Optional[str] = None) -> Dict[str, Any]:
    """Загружает пользовательские настройки из JSON.

    Args:
        path (str, optional): Путь к файлу настроек. По умолчанию берётся BASE_DIR/user_settings.json.

    Returns:
        dict: Словарь с настройками.

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    if path is None:
        path = os.path.join(BASE_DIR, "user_settings.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Настройки не найдены: {path}")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_main_page(date_str: str, stock_api_key: str) -> Dict[str, Any]:
    """Формирует данные для главной страницы:
    приветствие, карты, транзакции, валюты и акции.

    Args:
        date_str (str): Дата в формате "%Y-%m-%d %H:%M:%S".
        stock_api_key (str): API-ключ AlphaVantage.

    Returns:
        dict: Данные для отображения на главной странице.
    """
    date = parse_date(date_str)
    start_date, end_date = get_date_range(date, 'M')

    greeting = get_greeting(date)
    user_settings = get_user_settings()
    df = load_operations()

    cards_info = analyze_cards(df, start_date, end_date)
    top_transactions = get_top_transactions(df, start_date, end_date)

    currency_rates = get_currency_rates(
        user_settings["user_currencies"],
        base=user_settings.get("base_currency", "RUB"),
        access_key=user_settings.get("currency_api_key")
    )
    stock_prices = get_stock_prices(user_settings["user_stocks"], api_key=stock_api_key)

    return {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": [
            {"currency": c, "rate": rate} for c, rate in currency_rates.items()
        ],
        "stock_prices": [
            {"stock": s, "price": price} for s, price in stock_prices.items()
        ]
    }
