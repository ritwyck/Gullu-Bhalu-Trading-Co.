import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data, _get_live, _get_symbols_from_query, _set_symbols_in_query
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def render_compare_stocks(symbols: list[str]):
    st.title("📊 Trade Jockey Dashboard - Compare Stocks")
    valid_data = {}
    for sym in symbols:
        df = _get_live(sym)
        if df is not None and not df.empty:
            valid_data[sym] = df
        else:
            st.warning(f"No live data found for {sym}. Skipping.")

    if not valid_data:
        st.error("No valid data found for any selected stocks.")
        return

    max_len = max(len(df) for df in valid_data.values())
    fixed_periods, ratio_ref_period = get_period_inputs(max_len)

    all_rows = []
    for sym, df in valid_data.items():
        vol_rows = compute_volatility_and_ratios(
            df, fixed_periods, ratio_ref_period)
        for row in vol_rows:
            row["Symbol"] = sym
            all_rows.append(row)

    if not all_rows:
        st.error("Volatility & ratio calculations unavailable for selected symbols.")
        return

    vol_df = pd.DataFrame(all_rows)
    st.subheader("Volatility & Ratio Comparison Table")
    st.dataframe(vol_df)

    # Plot each stock
    for sym, df in valid_data.items():
        st.markdown(f"### {sym} - Close Price Chart")
        df_for_plot = df.reset_index().rename(columns={"index": "Date"})
        plot_stock_metric(df_for_plot, "Close", None)
