import streamlit as st
import pandas as pd
from Beauty.modules.plot import plot_stock_metric

from Beauty.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from Beauty.modules.ui_controls import select_symbol, get_metric_and_window, get_period_inputs
from Beauty.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def single_stock_view():
    st.header("Single Stock - Volatility, Ratio & ADX")

    # Data loading
    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    symbols = get_symbols(files)
    symbol = select_symbol(symbols)
    df = load_symbol_data(data_folder, symbol, files)

    if df is None:
        st.error(f"No data found for symbol '{symbol}'.")
        return

    # Metric selection/plotting
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric")
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    # Period inputs
    fixed_periods, ratio_ref_period = get_period_inputs(len(df))

    # Table calculations
    vol_rows = compute_volatility_and_ratios(
        df, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df, fixed_periods)

    # Display tables
    st.subheader(f"{symbol} - Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))
    st.subheader(f"{symbol} - ADX Table (TradingView/Yahoo Style)")
    st.dataframe(pd.DataFrame(adx_rows))
