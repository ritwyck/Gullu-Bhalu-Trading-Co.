import urllib.parse
import pandas as pd
import streamlit as st
from Frontend.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from Frontend.modules.ui_controls import get_metric_and_window, get_period_inputs
from Frontend.modules.plot import plot_stock_metric
from Frontend.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def render_single_stock(data_folder="Vault/Historical_Stock_Data"):
    """Render the single stock analysis page."""
    files = get_stock_files(data_folder)
    symbols = get_symbols(files)

    # --- URL param handling ---
    params = st.query_params
    default_symbol = params.get("symbol", symbols[0])
    if isinstance(default_symbol, list):
        default_symbol = default_symbol[0]

    # --- User select ---
    symbol = st.selectbox(
        "Select stock symbol",
        symbols,
        index=symbols.index(
            default_symbol) if default_symbol in symbols else 0,
    )

    # Update URL
    st.query_params["symbol"] = symbol

    # --- Load data ---
    df = load_symbol_data(data_folder, symbol, files)
    if df is None:
        st.error(f"No data found for symbol '{symbol}'.")
        return

    # --- Plotting ---
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    # --- Volatility & Ratios ---
    fixed_periods, ratio_ref_period = get_period_inputs(len(df))
    vol_rows = compute_volatility_and_ratios(
        df, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df, fixed_periods)

    # --- Display ---
    st.subheader(f"{symbol} - Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))

    st.subheader(f"{symbol} - ADX Table")
    st.dataframe(pd.DataFrame(adx_rows))
