import json
import pathlib
from typing import Any, Callable, TextIO

import pandas as pd
import pytest

from src import reports
from src.utils import normalize_transactions


@pytest.fixture(scope="module")
def data() -> pd.DataFrame:
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    path = root_dir / "data" / "operations.xlsx"

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    df = pd.read_excel(path)
    return normalize_transactions(df)


@pytest.mark.parametrize(
    "func, args, filename, expected_keys",
    [
        (
            reports.spending_by_category,
            ["2021-12"],
            "category.json",
            {"Категория", "Итого"},
        ),
        (
            reports.spending_by_weekday,
            [],  # только df + output_file
            "weekday.json",
            {"День недели", "Средний расход"},
        ),
        (
            reports.spending_by_workday,
            [],
            "workday.json",
            {"Тип дня", "Средний расход"},
        ),
    ],
)
def test_reports_generate_files(
    func: Callable[..., str],  # любая функция отчёта
    args: list[str],  # доп. аргументы
    filename: str,  # имя временного файла
    expected_keys: set[str],  # ключи в json
    data: pd.DataFrame,  # фикстура data
    tmp_path: pathlib.Path,  # встроенная фикстура pytest
) -> None:
    """Параметризованные тесты для отчетов"""
    output = tmp_path / filename
    result_path = func(data, *args, str(output))

    # функция должна вернуть путь (строку)
    assert isinstance(result_path, str)
    assert pathlib.Path(result_path).exists()

    with open(result_path, encoding="utf-8") as f:
        parsed = json.load(f)

    assert isinstance(parsed, list)
    assert expected_keys.issubset(parsed[0].keys())


def test_reports_with_mock(monkeypatch: pytest.MonkeyPatch, data: pd.DataFrame, tmp_path: pathlib.Path) -> None:
    called = {}

    def mock_dump(
        obj: Any,
        _fp: TextIO,
        _ensure_ascii: bool = False,
        _indent: int = 4,
    ) -> None:
        called["dumped"] = obj

    monkeypatch.setattr(json, "dump", mock_dump)

    output = tmp_path / "mocked.json"
    reports.spending_by_category(data, "2021-12", str(output))

    assert "dumped" in called
    assert isinstance(called["dumped"], list)
    assert "Категория" in called["dumped"][0]
