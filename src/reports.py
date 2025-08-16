import pandas as pd
import json
import logging
from functools import wraps
from typing import Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("reports.log"), logging.StreamHandler()]
)

def save_report(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результата отчета в JSON файл.

    Если filename не передан → создается имя вида report_<func>_<YYYYMMDD>.json
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Определяем имя файла
            out_file = filename
            if out_file is None:
                today = datetime.now().strftime("%Y%m%d")
                out_file = f"report_{func.__name__}_{today}.json"

            # Преобразуем DataFrame → JSON
            if isinstance(result, pd.DataFrame):
                json_result = result.to_json(orient="records", force_ascii=False, date_format="iso")
            else:
                json_result = json.dumps(result, ensure_ascii=False, indent=4)

            # Сохраняем
            Path(out_file).write_text(json_result, encoding="utf-8")
            logging.info(f"Отчет {func.__name__} сохранен в {out_file}")

            return result
        return wrapper
    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Отчет: траты по заданной категории за последние 3 месяца.

    :param transactions: датафрейм с транзакциями
    :param category: название категории
    :param date: опциональная дата (строка в формате YYYY-MM-DD), по умолчанию - сегодня
    :return: DataFrame с тратами по категории
    """
    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered = df[
        (df["Дата операции"].between(start_date, end_date)) &
        (df["Категория"] == category)
    ]

    return filtered[["Дата операции", "Категория", "Сумма операции"]]


@save_report()
def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Отчет: средние траты по дням недели за последние 3 месяца.

    :param transactions: датафрейм с транзакциями
    :param date: опциональная дата (строка в формате YYYY-MM-DD), по умолчанию - сегодня
    :return: DataFrame со средними тратами по дням недели
    """
    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered = df[df["Дата операции"].between(start_date, end_date)]
    filtered["weekday"] = filtered["Дата операции"].dt.day_name(locale="ru_RU")

    report = (
        filtered.groupby("weekday")["Сумма операции"]
        .mean()
        .reset_index()
        .rename(columns={"Сумма операции": "Средние траты"})
    )

    return report


@save_report()
def spending_by_workday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Отчет: средние траты в рабочий и выходной день за последние 3 месяца.

    :param transactions: датафрейм с транзакциями
    :param date: опциональная дата (строка в формате YYYY-MM-DD), по умолчанию - сегодня
    :return: DataFrame со средними тратами по рабочим/выходным дням
    """
    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered = df[df["Дата операции"].between(start_date, end_date)]
    filtered["is_weekend"] = filtered["Дата операции"].dt.weekday >= 5

    report = (
        filtered.groupby("is_weekend")["Сумма операции"]
        .mean()
        .reset_index()
        .replace({True: "Выходной", False: "Рабочий"})
        .rename(columns={"Сумма операции": "Средние траты", "is_weekend": "Тип дня"})
    )

    return report
