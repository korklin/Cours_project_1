from src.utils import (
    parse_date,
    get_date_range,
    get_greeting,
    get_user_settings
)
from src.reports import (
    analyze_cards,
    get_top_transactions,
    analyze_expenses,
    analyze_incomes,
    load_operations
)
from src.services import (
    get_currency_rates,
    get_stock_prices
)


def get_main_page(date_str: str):
    date = parse_date(date_str)
    start_date, end_date = get_date_range(date, 'M')

    greeting = get_greeting(date)
    user_settings = get_user_settings()

    # Здесь предполагаем, что операции хранятся в Excel
    cards_info = analyze_cards(start_date, end_date)
    top_transactions = get_top_transactions(start_date, end_date)
    currencies = get_currency_rates(user_settings["user_currencies"])
    stocks = get_stock_prices(user_settings["user_stocks"])

    return {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currencies": currencies,
        "stocks": stocks
    }


def get_events_page(date_str: str, range_type: str = "M"):
    date = parse_date(date_str)
    start_date, end_date = get_date_range(date, range_type)
    user_settings = get_user_settings()

    df = load_operations()

    expenses = analyze_expenses(start_date, end_date, df)
    incomes = analyze_incomes(start_date, end_date, df)

    currencies = {cur: 0.0 for cur in user_settings["user_currencies"]}
    stocks = {stock: 0.0 for stock in user_settings["user_stocks"]}

    return {
        "expenses": expenses,
        "incomes": incomes,
        "currencies": currencies,
        "stocks": stocks
    }