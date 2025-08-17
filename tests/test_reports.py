import json
import pathlib

import pandas as pd
import pytest

from src import reports
from src.utils import normalize_transactions


@pytest.fixture(scope="module")
def data():
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    path = root_dir / "data" / "operations.xlsx"

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    df = pd.read_excel(path)
    return normalize_transactions(df)


def test_spending_by_category_creates_file(data, tmp_path):
    output = tmp_path / "category.json"
    reports.spending_by_category(data, "2021-12", str(output))

    with open(output, encoding="utf-8") as f:
        parsed = json.load(f)

    assert isinstance(parsed, list)
    assert "Категория" in parsed[0]
    assert "Итого" in parsed[0]


def test_spending_by_weekday_creates_file(data, tmp_path):
    output = tmp_path / "weekday.json"
    reports.spending_by_weekday(data, str(output))

    with open(output, encoding="utf-8") as f:
        parsed = json.load(f)

    assert isinstance(parsed, list)
    assert "День недели" in parsed[0]
    assert "Средний расход" in parsed[0]


def test_spending_by_workday_creates_file(data, tmp_path):
    output = tmp_path / "workday.json"
    reports.spending_by_workday(data, str(output))

    with open(output, encoding="utf-8") as f:
        parsed = json.load(f)

    assert isinstance(parsed, list)
    assert "Тип дня" in parsed[0]
    assert "Средний расход" in parsed[0]
