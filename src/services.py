import requests
import yfinance as yf

def get_currency_rates(currencies: list, base: str = "RUB") -> dict:
    url = "https://api.exchangerate.host/latest"
    params = {"base": base, "symbols": ",".join(currencies)}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {cur: round(data["rates"].get(cur, 0), 4) for cur in currencies}
    except Exception as e:
        print(f"[Currency API error] {e}")
        return {cur: 0.0 for cur in currencies}


def get_stock_prices(tickers: list) -> dict:
    try:
        data = yf.download(tickers, period="1d", interval="1d", progress=False)
        if isinstance(data, dict) or "Close" not in data:
            return {ticker: 0.0 for ticker in tickers}
        if isinstance(data["Close"], pd.Series):
            return {tickers[0]: round(data["Close"].iloc[-1], 2)}
        return {ticker: round(data["Close"][ticker].iloc[-1], 2) for ticker in tickers}
    except Exception as e:
        print(f"[Stock API error] {e}")
        return {ticker: 0.0 for ticker in tickers}

