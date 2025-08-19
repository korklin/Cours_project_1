import json
from typing import Any

import pandas as pd
import pytest
from pandas import DataFrame

from src import services
from src.utils import normalize_transactions


@pytest.fixture
def dummy_df() -> DataFrame:
    df = pd.DataFrame(
        [
            {
                "Дата операции": "2021-12-21 10:00:00",
                "Сумма операции": -500,
                "Категория": "Супермаркет",
                "Описание": "Покупка продуктов",
            },
            {
                "Дата операции": "2021-12-22 12:00:00",
                "Сумма операции": -1500,
                "Категория": "Переводы",
                "Описание": "Перевод другу Ивану",
            },
            {
                "Дата операции": "2021-12-23 15:30:00",
                "Сумма операции": -200,
                "Категория": "Связь",
                "Описание": "Оплата телефона +79991234567",
            },
        ]
    )
    return normalize_transactions(df)


@pytest.mark.parametrize(
    "func,args,expected_type",
    [
        (services.cashback_analysis, (2021, 12), dict),
        (services.investment_bank, ("2021-12", 50), float),
        (services.simple_search, ("Супермаркет",), list),
        (services.search_phone_numbers, (), list),
        (services.search_person_transfers, (), list),
    ],
)
def test_services_parametrized(func: Any, args: dict[str, Any], expected_type: type, dummy_df: pd.DataFrame) -> None:
    """Проверяем все сервисы параметризованно"""
    if func is services.investment_bank:
        result = func("2021-12", dummy_df, 50)
        assert isinstance(result, float)
    elif func is services.simple_search:
        result = func("Супермаркет", dummy_df)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
    else:
        result = func(dummy_df, *args)
        parsed = json.loads(result)
        assert isinstance(parsed, expected_type)


def test_simple_search_with_mock(monkeypatch: pytest.MonkeyPatch, dummy_df: pd.DataFrame) -> None:
    # Мокаем метод DataFrame.to_json
    monkeypatch.setattr(pd.DataFrame, "to_json", lambda *a, **kw: "MOCKED_JSON")

    result = services.simple_search("Супермаркет", dummy_df)
    assert result == "MOCKED_JSON"


def test_cashback_analysis_with_mock(monkeypatch: pytest.MonkeyPatch, dummy_df: pd.DataFrame) -> None:
    """Мокаем json.loads, чтобы проверить правильность структуры"""
    monkeypatch.setattr("src.services.json.loads", lambda s: {"mocked": True})

    result = services.cashback_analysis(dummy_df, 2021, 12)
    parsed = json.loads(result)

    assert parsed == {"mocked": True}
