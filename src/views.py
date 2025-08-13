import json
import os
from datetime import datetime, timedelta, time
from typing import Any

import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

def get_date_range(date: datetime, range_type: str):
    if range_type == "W":
        start = date - timedelta(days=date.weekday())
        end = date
    elif range_type == "M":
        start = date.replace(day=1)
        end = date
    elif range_type == "Y":
        start = date.replace(month=1, day=1)
        end = date
    elif range_type == "ALL":
        start = datetime(2000, 1, 1)  # или earliest date
        end = date
    else:
        raise ValueError("Invalid range_type")
    return start, end

def get_greeting(date: datetime):
    hour = date.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def load_operations() -> pd.DataFrame:
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
    # Приведение сумм к числовому типу
    df["amount"] = df["amount"].astype(float)
    df["cashback"] = df["cashback"].astype(float)
    # Оформление карты: оставляем последние 4 цифры
    df["card_last4"] = df["card_number"].astype(str).str[-4:]
    return df

def analyze_cards(df: pd.DataFrame, start_date, end_date):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Ожидался DataFrame, а не datetime")

    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    cards = []
    for card, sub in df_range.groupby("card_last4"):
        total = sub["amount"].sum()
        cashback = total // 100  # 1 рубль на каждые 100 руб.
        cards.append({
            "card_last4": card,
            "total_spent": round(total, 2),
            "cashback": int(cashback)
        })
    return cards

def get_top_transactions(df: pd.DataFrame, start_date, end_date, n=5):
    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    top = df_range.nlargest(n, "amount")
    return top[["date", "card_last4", "amount", "category", "description"]].to_dict(orient="records")

def analyze_expenses(start_date, end_date, df=None):
    if df is None:
        df = load_operations()

    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    df_exp = df_range[df_range["amount"] < 0].copy()

    total_expense = -df_exp["amount"].sum()

    # Категории с наибшими тратами
    top_categories = (
        df_exp.groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )

    top7 = top_categories[:7]
    other = top_categories[7:].sum()

    main_section = [{"category": cat, "amount": int(val)} for cat, val in top7.items()]
    if other > 0:
        main_section.append({"category": "Остальное", "amount": int(other)})

    # Переводы и наличные
    cash_section = df_exp[df_exp["category"].isin(["Переводы", "Наличные"])]
    cash_summary = (
        cash_section.groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )

    cash_result = [
        {"category": row["category"], "amount": int(row["amount"])}
        for _, row in cash_summary.iterrows()
    ]

    return {
        "total": int(total_expense),
        "main": main_section,
        "cash_and_transfers": cash_result
    }


def analyze_incomes(start_date, end_date, df=None):
    if df is None:
        df = load_operations()

    df_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    df_inc = df_range[df_range["amount"] > 0].copy()

    total_income = df_inc["amount"].sum()

    grouped = (
        df_inc.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    main_section = [
        {"category": row["category"], "amount": int(row["amount"])}
        for _, row in grouped.iterrows()
    ]

    return {
        "total": int(total_income),
        "main": main_section
    }


def get_financial_data(currencies, stocks, access_key="fKCxXBg8fAPezuC0GlMI64lVbA4XloSU", timeout=60):
    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": access_key}

    # Запрос для валют
    params = {"currencies": ",".join(currencies), "stocks": ",".join(stocks)}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        print("API response:", data)  # Добавьте вывод ответа API

        if not data.get("success", False):
            raise ValueError(data.get("error", {}).get("info", "Unknown error"))

        currencies_data = {cur: round(data["rates"].get(cur, 0), 4) for cur in currencies}
        stocks_data = {stock: round(data["stocks"].get(stock, {}).get("price", 0), 2) for stock in stocks}

        return currencies_data, stocks_data
    except requests.exceptions.Timeout:
        print("[Financial API error] Timeout exceeded")
        return {cur: 0.0 for cur in currencies}, {stock: 0.0 for stock in stocks}
    except requests.exceptions.RequestException as e:
        print(f"[Financial API error] {e}")
        return {cur: 0.0 for cur in currencies}, {stock: 0.0 for stock in stocks}
    except Exception as e:
        print(f"[Financial API error] Unexpected error: {e}")
        return {cur: 0.0 for cur in currencies}, {stock: 0.0 for stock in stocks}


def get_user_settings(path=None):
    if path is None:
        path = os.path.join(BASE_DIR, "user_settings.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Настройки не найдены: {path}")
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def get_main_page(date_str: str):
    date = parse_date(date_str)
    start_date, end_date = get_date_range(date, 'M')

    greeting = get_greeting(date)
    user_settings = get_user_settings()
    df = load_operations()
    # Здесь предполагаем, что операции хранятся в Excel
    cards_info = analyze_cards(df, start_date, end_date)
    top_transactions = get_top_transactions(df, start_date, end_date)
    currencies, stocks = get_financial_data(user_settings["user_currencies"], user_settings["user_stocks"])

    return {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currencies": currencies,
        "stocks": stocks
    }


def get_events_page(date_str: str, range_type: str = "M"):
    date = parse_date(date_str)
    start_date, end_date = get_date_range(date, range_type)
    user_settings = get_user_settings()

    df = load_operations()

    expenses = analyze_expenses(df, start_date, end_date)
    incomes = analyze_incomes(df, start_date, end_date)

    currencies = {cur: 0.0 for cur in user_settings["user_currencies"]}
    stocks = {stock: 0.0 for stock in user_settings["user_stocks"]}

    return {
        "expenses": expenses,
        "incomes": incomes,
        "currencies": currencies,
        "stocks": stocks
    }


def get_currency_rates(currencies, base="RUB", access_key= "fKCxXBg8fAPezuC0GlMI64lVbA4XloSU"):
    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": access_key}
    params = {
        "base": base,
        "symbols": ",".join(currencies)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", False):
            raise ValueError(data.get("error", {}).get("info", "Unknown error"))
        return {cur: round(data["rates"].get(cur, 0), 4) for cur in currencies}
    except Exception as e:
        print(f"[Currency API error] {e}")
        return {cur: 0.0 for cur in currencies}


def get_stock_prices(tickers: list, access_key="fKCxXBg8fAPezuC0GlMI64lVbA4XloSU"):
    url = "https://api.apilayer.com/stocks/latest"
    headers = {"apikey": access_key}
    params = {"symbols": ",".join(tickers)}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", False):
            raise ValueError(data.get("error", {}).get("info", "Unknown error"))

        # Предположим, что структура данных в API apilayer.com схожа с валютным API
        return {ticker: round(data["data"].get(ticker, {}).get("price", 0), 2) for ticker in tickers}
    except Exception as e:
        print(f"[Stock API error] {e}")
        return {ticker: 0.0 for ticker in tickers}


