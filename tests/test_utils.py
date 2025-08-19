from typing import Any, Generator

import pandas as pd
import pytest

from src.utils import prepare_events


# --- ПАРАМЕТРИЗОВАННЫЙ ТЕСТ ---
@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            [
                {
                    "Дата операции": "2021-12-21 10:00:00",
                    "Сумма операции": -500,
                    "Категория": "Еда",
                    "Описание": "Покупка в магазине",
                }
            ],
            {
                "дата": "21.12.2021 10:00:00",
                "сумма": -500,
                "категория": "Еда",
                "описание": "Покупка в магазине",
            },
        ),
        (
            [
                {
                    "Дата операции": "2021-12-22 15:30:00",
                    "Сумма операции": -1200,
                    "Категория": "Транспорт",
                    "Описание": "Такси",
                }
            ],
            {
                "дата": "22.12.2021 15:30:00",
                "сумма": -1200,
                "категория": "Транспорт",
                "описание": "Такси",
            },
        ),
    ],
)
def test_prepare_events_parametrized(input_data: list[dict[str, str | int]], expected: dict[str, str | int]) -> None:
    """Проверяем разные сценарии через параметризацию"""
    df = pd.DataFrame(input_data)
    events = prepare_events(df)

    assert isinstance(events, list)
    assert events[0] == expected


# --- ТЕСТ С МОКАМИ ---
def test_prepare_events_with_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Подменяем pd.DataFrame заглушкой"""

    class DummyDF:
        def iterrows(self) -> Generator[tuple[int, dict[str, str | int]], Any, None]:
            yield 0, {
                "Дата операции": "2021-12-21 10:00:00",
                "Сумма операции": -500,
                "Категория": "Еда",
                "Описание": "Покупка в магазине",
            }

    # monkeypatch заменяет pd.DataFrame в src.utils на DummyDF
    monkeypatch.setattr("src.utils.pd.DataFrame", lambda *a, **kw: DummyDF())

    df = pd.DataFrame([])  # вернется DummyDF
    events = prepare_events(df)

    assert len(events) == 1
    assert events[0]["категория"] == "Еда"
    assert events[0]["сумма"] == -500
