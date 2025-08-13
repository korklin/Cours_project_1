from src.services import get_currency_rates, get_stock_prices


def test_get_currency_rates(monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self): pass

            def json(self): return {"rates": {"USD": 90.0, "EUR": 98.0}}

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    result = get_currency_rates(["USD", "EUR"])
    assert result == {"USD": 90.0, "EUR": 98.0}


def test_get_stock_prices(monkeypatch):
    import pandas as pd
    from pandas import MultiIndex

    def mock_download(tickers, **kwargs):
        index = pd.date_range("2025-08-12", periods=1)
        columns = MultiIndex.from_product([['Close'], tickers])
        data = pd.DataFrame([[200 + i for i in range(len(tickers))]], index=index, columns=columns)
        return data

    monkeypatch.setattr("yfinance.download", mock_download)
    result = get_stock_prices(["AAPL", "TSLA"])
    assert "AAPL" in result
    assert isinstance(result["AAPL"], float)