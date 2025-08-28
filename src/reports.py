import json
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def spending_by_category(
    df: pd.DataFrame, month: str, output_file: str = "report_by_category.json"
) -> str:
    """
    Считает расходы по категориям за указанный месяц.
    month: '2021-12'
    """
    df = df.copy()
    df["Месяц"] = df["Дата операции"].dt.to_period("M").astype(str)
    filtered = df[df["Месяц"] == month]

    report = (
        filtered.groupby("Категория")["Сумма операции"]
        .sum()
        .reset_index()
        .rename(columns={"Категория": "Категория", "Сумма операции": "Итого"})
    )

    path = os.path.join(BASE_DIR, "reports", output_file)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    return path


def spending_by_weekday(
    df: pd.DataFrame, output_file: str = "report_by_weekday.json"
) -> str:
    """
    Считает средние расходы по дням недели.
    """
    df = df.copy()
    df["День недели"] = df["Дата операции"].dt.day_name(locale="ru_RU")

    report = (
        df.groupby("День недели")["Сумма операции"]
        .mean()
        .reset_index()
        .rename(columns={"Сумма операции": "Средний расход"})
    )

    path = os.path.join(BASE_DIR, "reports", output_file)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    return path


def spending_by_workday(
    df: pd.DataFrame, output_file: str = "report_by_workday.json"
) -> str:
    """
    Считает расходы в будни и выходные.
    """
    df = df.copy()
    df["Тип дня"] = df["Дата операции"].dt.weekday.apply(
        lambda x: "Будни" if x < 5 else "Выходные"
    )

    report = (
        df.groupby("Тип дня")["Сумма операции"]
        .mean()
        .reset_index()
        .rename(columns={"Сумма операции": "Средний расход"})
    )

    path = os.path.join(BASE_DIR, "reports", output_file)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    return path
