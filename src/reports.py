import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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