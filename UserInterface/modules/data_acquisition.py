from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd


def fetch_historical_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data on demand only (not stored permanently).
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
