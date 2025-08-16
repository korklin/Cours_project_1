import os
import glob
import json
import pandas as pd
import pytest
from src import reports


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми транзакциями."""
    data = {
        "Дата операции": pd.to_datetime([
            "2024-05-01", "2024-05-03", "2024-05-05",
            "2024-06-10", "2024-06-12", "2024-07-01",
        ]),
        "Категория": [
            "Продукты", "Кафе", "Продукты",
            "Транспорт", "Продукты", "Кафе",
        ],
        "Сумма операции": [1000, 500, 1500, 200, 800, 700],
    }
    return pd.DataFrame(data)


def find_report_file(func_name: str) -> str:
    """Находит последний созданный отчёт по имени функции."""
    files = glob.glob(f"report_{func_name}_*.json")
    assert files, f"Файл для {func_name} не найден"
    return max(files, key=os.path.getctime)


def read_json_file(file_path: str) -> list:
    """Чтение JSON-файла и возврат содержимого."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_spending_by_category_creates_file(sample_data):
    """Проверка трат по категории и создания JSON-файла."""
    result = reports.spending_by_category(sample_data, "Продукты", date="2024-07-10")

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "Категория" in result.columns

    file_path = find_report_file("spending_by_category")
    content = read_json_file(file_path)
    assert isinstance(content, list)
    assert len(content) > 0


def test_spending_by_weekday_creates_file(sample_data):
    """Проверка трат по дням недели и создания JSON-файла."""
    result = reports.spending_by_weekday(sample_data, date="2024-07-10")

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "weekday" in result.columns

    file_path = find_report_file("spending_by_weekday")
    content = read_json_file(file_path)
    assert isinstance(content, list)
    assert len(content) > 0


def test_spending_by_workday_creates_file(sample_data):
    """Проверка трат по рабочим/выходным дням и создания JSON-файла."""
    result = reports.spending_by_workday(sample_data, date="2024-07-10")

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "Тип дня" in result.columns  # фикс: проверяем реальное имя столбца

    file_path = find_report_file("spending_by_workday")
    content = read_json_file(file_path)
    assert isinstance(content, list)
    assert len(content) > 0
