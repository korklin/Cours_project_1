import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _to_json(df: pd.DataFrame) -> str:
    """
    Конвертирует DataFrame в JSON, приводя все даты к строкам.
    """
    df_copy = df.copy()

    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].astype(str)

    return df_copy.to_json(orient="records", force_ascii=False, indent=4)

def cashback_analysis(data: pd.DataFrame, year: int, month: int) -> str:
    """
    Анализ выгодности категорий повышенного кешбэка.

    Args:
        data (pd.DataFrame): Данные с транзакциями (из Excel).
        year (int): Год для анализа.
        month (int): Месяц для анализа.

    Returns:
        str: JSON с анализом, сколько можно заработать кешбэка в каждой категории.
             Формат:
             {
                 "Категория 1": 1000.0,
                 "Категория 2": 2000.0
             }
    """
    try:
        # Преобразуем даты в корректный формат (день.месяц.год часы:минуты:секунды)
        data["Дата операции"] = pd.to_datetime(
            data["Дата операции"],
            format="%d.%m.%Y %H:%M:%S",
            errors="coerce"
        )

        # Фильтруем по указанному году и месяцу
        filtered = data[
            (data["Дата операции"].dt.year == year) &
            (data["Дата операции"].dt.month == month)
        ]

        if filtered.empty:
            logger.warning(f"Нет данных за {year}-{month:02d}")
            return json.dumps({}, ensure_ascii=False, indent=4)

        # Группируем по категории и суммируем кешбэк
        result = (
            filtered.groupby("Категория")
            ["Бонусы (включая кэшбэк)"]
            .sum()
            .to_dict()
        )

        logger.info(f"Анализ кешбэка за {year}-{month:02d} выполнен успешно")
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при анализе кешбэка: {e}")
        raise


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
    Поиск по описанию или категории.
    """
    mask = data["Описание"].str.contains(query, case=False, na=False) | \
           data["Категория"].str.contains(query, case=False, na=False)
    return _to_json(data[mask])


def search_phone_numbers(data: pd.DataFrame) -> str:
    """
    Поиск транзакций, содержащих телефонные номера в описании.

    Аргументы:
        data: DataFrame с транзакциями.

    Возвращает:
        JSON-строку с транзакциями, где найдены телефонные номера.
    """
    phone_pattern = r"\+7\s?\d{3}\s?\d{2,3}-?\d{2}-?\d{2}"
    mask = data["Описание"].str.contains(phone_pattern, regex=True, na=False)
    result = data[mask]
    return _to_json(result)


def search_person_transfers(data: pd.DataFrame) -> str:
    """
    Поиск переводов физическим лицам (категория 'Переводы',
    описание содержит имя и инициал).
    """
    person_pattern = re.compile(r"[А-ЯЁ][а-яё]+ [А-Я]\.")
    mask = (data["Категория"] == "Переводы") & \
           data["Описание"].str.contains(person_pattern, na=False)
    return _to_json(data[mask])
