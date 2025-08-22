import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


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
    st.experimental_set_query_params(symbol=symbols)


def render_single_stock(symbol: str):
    df_live = _get_live(symbol)
    if df_live is None or df_live.empty:
        st.error(f"No live historical data found for '{symbol}'.")
        return

    recent_df = df_live.tail(30)
    ohlc_cols = [c for c in ["Open", "High",
                             "Low", "Close"] if c in df_live.columns]
    if not recent_df.empty and ohlc_cols:
        st.subheader(f"{symbol} Data")
        st.dataframe(recent_df.loc[:, ohlc_cols])
    else:
        st.info("No OHLC data available.")

    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    df_for_plot = df_live.reset_index().rename(columns={"index": "Date"})
    plot_stock_metric(df_for_plot, metric, window if metric ==
                      "Volatility" else None)

    fixed_periods, ratio_ref_period = get_period_inputs(len(df_live))
    vol_rows = compute_volatility_and_ratios(
        df_live, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df_live, fixed_periods)

    if vol_rows:
        st.subheader(f"{symbol} — Volatility & Ratio Table")
        st.dataframe(pd.DataFrame(vol_rows))
    else:
        st.info("Volatility & ratio calculations unavailable for this symbol.")

    if adx_rows:
        st.subheader(f"{symbol} — ADX Table")
        st.dataframe(pd.DataFrame(adx_rows))
    else:
        st.info("ADX calculations unavailable for this symbol.")


def main():
    st.set_page_config(page_title="Trade Jockey Dashboard", layout="wide")
    st.title("📈 Trade Jockey Dashboard - Single Stock")

    symbols = _get_symbols_from_query()
    symbol = symbols[0] if symbols else None

    # Top-page search bar and match picker
    search_query = st.text_input(
        "🔎 Search company name or symbol", key="search_text_single")
    if search_query:
        matches = search_symbols(search_query)
        if matches:
            st.write("Matching companies and symbols:")
            for sym, desc in matches:
                if st.button(f"{sym} — {desc}", key=f"btn_single_{sym}"):
                    _set_symbols_in_query([sym])
                    st.experimental_rerun()
        else:
            st.warning("No matches found.")

    if not symbol:
        st.info("Please search and select a company symbol above to proceed.")
        return

    render_single_stock(symbol)


if __name__ == "__main__":
    main()
