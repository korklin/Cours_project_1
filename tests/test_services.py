import json
import pathlib

import pandas as pd
import pytest

from src import services
from src.utils import normalize_transactions


@pytest.fixture(scope="module")
def data():
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    path = root_dir / "data" / "operations.xlsx"

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    df = pd.read_excel(path)
    return normalize_transactions(df)


def test_cashback_analysis(data):
    result = services.cashback_analysis(data, 2021, 12)
    parsed = json.loads(result)

    assert isinstance(result, str)
    assert isinstance(parsed, dict)
    assert len(parsed) > 0


def test_investment_bank(data):
    result = services.investment_bank("2021-12", data, 50)
    assert isinstance(result, float)
    assert result >= 0


def test_simple_search(data):
    result = services.simple_search("Супермаркет", data)
    parsed = json.loads(result)

    assert isinstance(result, str)
    assert isinstance(parsed, list)
    assert any(
        "Супермаркет" in tx.get("Описание", "")
        or "Супермаркет" in tx.get("Категория", "")
        for tx in parsed
    )


def test_search_phone_numbers(data):
    result = services.search_phone_numbers(data)
    parsed = json.loads(result)

    assert isinstance(result, str)
    assert isinstance(parsed, list)


def test_search_person_transfers(data):
    result = services.search_person_transfers(data)
    parsed = json.loads(result)

    assert isinstance(result, str)
    assert isinstance(parsed, list)
    assert all(
        "Перевод" in tx.get("Категория", "")
        or "перевод" in tx.get("Описание", "").lower()
        for tx in parsed
    )
