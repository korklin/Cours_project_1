import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cashback_analysis(data: pd.DataFrame, year: int, month: int) -> str:
    """
    Анализ выгодных категорий повышенного кешбэка за конкретный месяц.

    :param data: DataFrame с транзакциями
    :param year: год анализа
    :param month: месяц анализа
    :return: JSON-строка с категориями и суммой начисленного кешбэка
    """
    logger.info(f"Анализ кешбэка за {year}-{month:02d}")

    # фильтрация по дате
    data["Дата операции"] = pd.to_datetime(data["Дата операции"], errors="coerce")
    df_filtered = data[
        (data["Дата операции"].dt.year == year)
        & (data["Дата операции"].dt.month == month)
    ]

    # группировка по категориям
    result = (
        df_filtered.groupby("Категория")["Бонусы (включая кэшбэк)"]
        .sum()
        .astype(int)
        .to_dict()
    )

    return json.dumps(result, ensure_ascii=False, indent=4)


def investment_bank(month: str, transactions: pd.DataFrame, limit: int) -> float:
    """
    Рассчитывает сумму, которая попала бы в "Инвесткопилку" за указанный месяц.

    :param month: месяц в формате 'YYYY-MM'
    :param transactions: DataFrame с транзакциями
    :param limit: шаг округления (10, 50, 100 ₽)
    :return: сумма накоплений
    """
    logger.info(f"Расчёт инвесткопилки за {month}, шаг округления {limit}")

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], errors="coerce"
    )
    year, month_num = map(int, month.split("-"))

    df_filtered = transactions[
        (transactions["Дата операции"].dt.year == year)
        & (transactions["Дата операции"].dt.month == month_num)
    ]

    # считаем вручную разницу до ближайшего limit
    diffs = df_filtered["Сумма операции"].apply(
        lambda x: (limit - (abs(x) % limit)) % limit if x < 0 else 0
    )

    return float(diffs.sum())


def simple_search(query: str, data: pd.DataFrame) -> str:
    """
    Простой поиск по описанию и категории.

    :param query: строка для поиска
    :param data: DataFrame с транзакциями
    :return: JSON со всеми транзакциями, где найдено совпадение
    """
    logger.info(f"Поиск по строке: {query}")

    mask = data["Описание"].str.contains(query, case=False, na=False) | \
           data["Категория"].str.contains(query, case=False, na=False)

    result = data[mask].to_dict(orient="records")
    return json.dumps(result, ensure_ascii=False, indent=4)


def search_phone_numbers(data: pd.DataFrame) -> str:
    """
    Поиск транзакций с мобильными номерами в описании.

    :param data: DataFrame с транзакциями
    :return: JSON со всеми транзакциями с номерами
    """
    logger.info("Поиск номеров телефонов")

    phone_pattern = re.compile(r"\+7\s?\d{3}[\s-]?\d{2,3}[\s-]?\d{2}[\s-]?\d{2}")

    mask = data["Описание"].str.contains(phone_pattern, na=False)
    result = data[mask].to_dict(orient="records")
    return json.dumps(result, ensure_ascii=False, indent=4)


def search_person_transfers(data: pd.DataFrame) -> str:
    """
    Поиск переводов физическим лицам (категория 'Переводы' + имя и инициал).

    :param data: DataFrame с транзакциями
    :return: JSON со всеми переводами физлицам
    """
    logger.info("Поиск переводов физическим лицам")

    pattern = re.compile(r"[А-ЯЁ][а-яё]+ [А-ЯЁ]\.")
    mask = (data["Категория"] == "Переводы") & data["Описание"].str.contains(pattern, na=False)

    result = data[mask].to_dict(orient="records")
    return json.dumps(result, ensure_ascii=False, indent=4)
