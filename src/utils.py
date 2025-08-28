import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Загружаем операции из Excel.
    """
    try:
        df = pd.read_excel(filepath)
        logger.info(f"Файл {filepath} успешно загружен")
        return df
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла {filepath}: {e}")
        return pd.DataFrame()


def normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Нормализует данные из Excel: проверяет наличие нужных колонок,
    приводит типы и заменяет NaN.
    """
    required_cols = ["Дата операции", "Сумма операции", "Категория", "Описание"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Приведение типов
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], errors="coerce", dayfirst=True
    )
    df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce").fillna(
        0.0
    )

    # Заполнение пропусков
    df["Категория"] = df["Категория"].fillna("Неизвестно")
    df["Описание"] = df["Описание"].fillna("")

    # Кэшбэк
    if "Кэшбэк" not in df.columns:
        df["Кэшбэк"] = 0.0
    else:
        df["Кэшбэк"] = pd.to_numeric(df["Кэшбэк"], errors="coerce").fillna(0.0)

    return df


def prepare_events(df: pd.DataFrame) -> list[dict]:
    """
    Преобразует DataFrame транзакций в список событий для страницы "События".
    """
    events = []
    for _, row in df.iterrows():
        raw_date = row["Дата операции"]

        parsed_date = None
        if isinstance(raw_date, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
                try:
                    parsed_date = datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue
        elif isinstance(raw_date, pd.Timestamp):
            parsed_date = raw_date.to_pydatetime()

        events.append(
            {
                "дата": (
                    parsed_date.strftime("%d.%m.%Y %H:%M:%S") if parsed_date else ""
                ),
                "сумма": row["Сумма операции"],
                "категория": row["Категория"],
                "описание": row["Описание"],
            }
        )
    return events
