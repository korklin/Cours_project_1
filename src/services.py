from typing import Any

import pandas as pd
import requests
import time
import yfinance as yf

def get_currency_rates(currencies, base="RUB", access_key= "fKCxXBg8fAPezuC0GlMI64lVbA4XloSU"):
    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": access_key}
    params = {
        "base": base,
        "symbols": ",".join(currencies)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", False):
            raise ValueError(data.get("error", {}).get("info", "Unknown error"))
        return {cur: round(data["rates"].get(cur, 0), 4) for cur in currencies}
    except Exception as e:
        print(f"[Currency API error] {e}")
        return {cur: 0.0 for cur in currencies}


def get_stock_prices(tickers: list, max_retries=3, delay=1) -> dict[Any, Any] | dict[Any, float] | None:
    for attempt in range(max_retries):
        try:
            data = yf.download(tickers, period="1d", interval="1d", progress=False, auto_adjust=True)
            if isinstance(data, dict) or "Close" not in data:
                raise ValueError("No Close data in yf response")

            if isinstance(data["Close"], pd.Series):
                return {tickers[0]: round(data["Close"].iloc[-1], 2)}

            return {ticker: round(data["Close"][ticker].iloc[-1], 2) for ticker in tickers}

        except Exception as e:
            print(f"[Stock API error attempt {attempt+1}] {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                return None
            else:
                # Последняя попытка — возвращаем нули
                return {ticker: 0.0 for ticker in tickers}
    return None

