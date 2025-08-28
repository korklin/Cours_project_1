import json

import pandas as pd


def cashback_analysis(df: pd.DataFrame, year: int, month: int) -> str:
    """
    Анализ выгодных категорий кешбэка.
    """
    df = df.copy()
    df = df[
        (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
    ]

    grouped = df.groupby("Категория")["Кэшбэк"].sum().reset_index()
    result = {row["Категория"]: float(row["Кэшбэк"]) for _, row in grouped.iterrows()}
    return json.dumps(result, ensure_ascii=False)


def investment_bank(month: str, df: pd.DataFrame, round_to: int = 100) -> float:
    """
    Инвесткопилка: округление расходов.
    """
    df = df.copy()
    df["Месяц"] = df["Дата операции"].dt.to_period("M").astype(str)
    df = df[df["Месяц"] == month]

    savings = 0.0
    for amount in df["Сумма операции"]:
        if amount < 0:
            remainder = (-amount) % round_to
            savings += remainder
    return float(savings)


def simple_search(query: str, df: pd.DataFrame) -> str:
    """
    Поиск по описанию или категории с приведением дат.
    """
    # Нормализуем даты
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], dayfirst=False, errors="coerce", format="%Y-%m-%d %H:%M:%S"
    )

    # Фильтруем по запросу
    result = df[
        df["Описание"].str.contains(query, case=False, na=False)
        | df["Категория"].str.contains(query, case=False, na=False)
    ]

    return result.to_json(orient="records", force_ascii=False)


def search_phone_numbers(df: pd.DataFrame) -> str:
    """
    Поиск операций с телефонными номерами.
    """
    mask = df["Описание"].str.contains(r"\+7\d{10}", na=False) | df[
        "Описание"
    ].str.contains(r"8\d{10}", na=False)
    result = df[mask]
    return result.to_json(orient="records", force_ascii=False)


def search_person_transfers(df: pd.DataFrame) -> str:
    """
    Поиск переводов физическим лицам.
    """
    mask = df["Категория"].str.contains("Перевод", na=False) | df[
        "Описание"
    ].str.contains("перевод", case=False, na=False)
    result = df[mask]
    return result.to_json(orient="records", force_ascii=False)
