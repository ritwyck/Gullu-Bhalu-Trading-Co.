import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data, _get_live, _get_symbols_from_query, _set_symbols_in_query
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def render_single_stock(symbol: str):
    df_live = _get_live(symbol)
    if df_live is None or df_live.empty:
        st.error(f"No live historical data found for '{symbol}'.")
        return

    # Raw OHLC display
    recent_df = df_live.tail(30)
    ohlc_cols = [c for c in ["Open", "High",
                             "Low", "Close"] if c in df_live.columns]
    if not recent_df.empty and ohlc_cols:
        st.subheader(f"{symbol} Data")
        st.dataframe(recent_df.loc[:, ohlc_cols])
    else:
        st.info("No OHLC data available.")

    # Metric selection and chart
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    df_for_plot = df_live.reset_index().rename(columns={"index": "Date"})
    plot_stock_metric(df_for_plot, metric, window if metric ==
                      "Volatility" else None)

    # Volatility & Ratio / ADX tables
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
