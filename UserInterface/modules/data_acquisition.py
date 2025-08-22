from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import streamlit as st


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


@st.cache_data(ttl=0, show_spinner=False)
def _get_live(symbol: str) -> pd.DataFrame | None:
    try:
        df = fetch_historical_data(symbol, period="2y", interval="1d")
        if df is None or df.empty:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].copy()
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert(None)
        return df.sort_index()
    except Exception:
        return None


def _get_symbols_from_query() -> list[str]:
    qp = st.query_params
    val = qp.get("symbol")
    if isinstance(val, str):
        return [val]
    elif isinstance(val, list):
        return val
    else:
        return []


def _set_symbols_in_query(symbols: list[str]) -> None:
    st.query_params["symbol"] = symbols
