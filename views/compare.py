import urllib.parse
import streamlit as st
from Frontend.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from Frontend.modules.ui_controls import get_period_inputs
from Frontend.modules.calculations import compute_multiple_volatility_ratios
import pandas as pd


def render_compare_stocks(data_folder="Vault/Historical_Stock_Data"):
    """Render the multi-stock comparison page."""
    files = get_stock_files(data_folder)
    all_symbols = get_symbols(files)

    # --- URL param handling ---
    params = st.query_params
    if "symbols" in params:
        raw = params["symbols"]
        selected_symbols = raw[0].split(",") if isinstance(
            raw, list) else raw.split(",")
    else:
        selected_symbols = all_symbols[:2]

    # --- User multiselect ---
    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare",
        all_symbols,
        default=selected_symbols,
        help="Select at least 2 and up to 10 stocks",
    )

    # 🚨 Enforce minimum
    if len(selected_symbols) < 2:
        st.warning("You must keep at least 2 stocks selected. Resetting...")
        selected_symbols = all_symbols[:2]
        st.experimental_rerun()

    # Update query params
    st.query_params["symbols"] = ",".join(selected_symbols)

    # --- Get user inputs ---
    first_df_len = len(load_symbol_data(
        data_folder, selected_symbols[0], files))
    custom_period, ratio_ref_period = get_period_inputs(first_df_len)

    # --- Compute ---
    final_df = compute_multiple_volatility_ratios(
        selected_symbols, files, data_folder, custom_period, ratio_ref_period
    )

    # Add links
    final_df["Stock"] = final_df["Symbol"].apply(
        lambda s: f"/?page=Stocks&symbol={urllib.parse.quote(s)}"
    )

    # Reorder
    cols = ["Symbol", "Stock"] + \
        [c for c in final_df.columns if c not in ["Symbol", "Stock"]]
    final_df = final_df[cols]

    # --- Display ---
    st.subheader("Volatility & Ratios Table")
    st.data_editor(
        final_df,
        column_config={
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
        },
        hide_index=True,
        key="compare_stocks_editor",
    )
