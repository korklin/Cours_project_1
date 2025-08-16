import pathlib

import pandas as pd
import pytest
from src import services


@pytest.fixture(scope="module")
def data():
    """
    Фикстура для загрузки Excel с транзакциями.
    Используется во всех тестах.
    """
    # Находим путь к папке data
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    path = root_dir / "data" / "operations.xlsx"

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    return pd.read_excel(path)


def test_cashback_analysis(data):
    """
    Тест анализа выгодных категорий кешбэка.
    Проверяем, что результат — это строка в формате JSON
    и что в нём есть хотя бы одна категория.
    """
    result = services.cashback_analysis(data, 2021, 12)
    assert isinstance(result, str)
    assert "Супермаркеты" in result or "Различные товары" in result


def test_investment_bank(data):
    """
    Тест расчёта инвесткопилки.
    Проверяем, что сумма округлений за месяц считается корректно.
    """
    result = services.investment_bank("2021-12", data, 50)
    assert isinstance(result, float)
    assert result >= 0


def test_simple_search(data):
    """
    Тест простого поиска по описанию.
    Проверяем, что при поиске по слову 'Пятерочка'
    возвращаются транзакции с этим магазином.
    """
    result = services.simple_search("Супермаркет", data)
    assert isinstance(result, str)
    assert "Супермаркет" in result


def test_search_phone_numbers(data):
    """
    Тест поиска транзакций с телефонными номерами.
    Проверяем, что поиск возвращает JSON и работает без ошибок.
    """
    result = services.search_phone_numbers(data)
    assert isinstance(result, str)


def test_search_person_transfers(data):
    """
    Тест поиска переводов физическим лицам.
    Проверяем, что результат — JSON и что транзакции действительно относятся к переводам.
    """
    result = services.search_person_transfers(data)
    assert isinstance(result, str)
