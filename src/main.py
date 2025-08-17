import json
import logging

import pandas as pd

from src.settings import LOG_LEVEL
from src.views import get_events_page, get_main_page

# Логирование
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(levelname)s:%(name)s:%(message)s",
)
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


if __name__ == "__main__":
    result_main = get_main_page("2021-12-21 10:00:00")
    print("=== Главная ===")
    print(json.dumps(result_main, ensure_ascii=False, indent=2))

    df = pd.DataFrame(
        [
            {
                "Дата операции": "2021-12-21 10:00:00",
                "Сумма операции": -100,
                "Категория": "Еда",
                "Описание": "Обед",
            }
        ]
    )
    result_events = get_events_page(df)
    print("=== События ===")
    print(json.dumps(result_events, ensure_ascii=False, indent=2))
