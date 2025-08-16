import pandas as pd
from src.utils import prepare_events


def test_prepare_events_returns_expected_format():
    df = pd.DataFrame(
        [
            {
                "Дата операции": "2021-12-21 10:00:00",
                "Сумма операции": -500,
                "Категория": "Еда",
                "Описание": "Покупка в магазине",
            },
            {
                "Дата операции": "2021-12-22 15:30:00",
                "Сумма операции": -1200,
                "Категория": "Транспорт",
                "Описание": "Такси",
            },
        ]
    )

    events = prepare_events(df)

    assert isinstance(events, list)
    assert all(isinstance(e, dict) for e in events)
    assert events[0]["дата"] == "21.12.2021 10:00:00"
    assert events[0]["сумма"] == -500
    assert events[0]["категория"] == "Еда"
    assert events[0]["описание"] == "Покупка в магазине"
    assert events[1]["категория"] == "Транспорт"
