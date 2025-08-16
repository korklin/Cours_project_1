import json
import pandas as pd
from src.views import get_main_page, get_events_page
from src.utils import prepare_events


def test_get_main_page_returns_str():
    result = get_main_page()
    assert isinstance(result, str)


def test_get_events_page_returns_json_dict():
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

    result = get_events_page(df)
    assert isinstance(result, dict)
    assert "events" in result
    assert len(result["events"]) > 0
