import os
import pandas as pd
import streamlit as st
import urllib.parse
from Frontend.modules.data_loading import load_symbol_data, get_stock_files, get_symbols
from Frontend.modules.calculations import compute_multiple_volatility_ratios
from Frontend.modules.ui_controls import get_period_inputs
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from Frontend.modules.page_config import set_page_config

set_page_config()

hide_default_nav()  # Hide the default multipage nav
selected_page = custom_sidebar()


def compare_stocks_view(selected_symbols=None):
    st.header("Multiple Stock Volatility Comparison")

    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    all_symbols = get_symbols(files)

    # Default selection from query params or first two symbols
    params = st.query_params
    if selected_symbols is None:
        if "symbols" in params:
            param_syms = params["symbols"]
            # params["symbols"] may be a comma-separated string or list
            if isinstance(param_syms, list):
                selected_symbols = param_syms[0].split(",")
            else:
                selected_symbols = param_syms.split(",")
        else:
            selected_symbols = all_symbols[:2]

    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare",
        all_symbols,
        default=selected_symbols,
        help="Select at least 2 and up to 10 stocks"
    )
    st.query_params["symbols"] = ",".join(selected_symbols)

    if len(selected_symbols) < 2:
        st.warning("Please select at least 2 stocks to compare.")
        return
    if len(selected_symbols) > 10:
        st.warning("Select up to 10 stocks only.")
        return

    # Get user period inputs
    first_df_len = len(load_symbol_data(
        data_folder, selected_symbols[0], files))
    custom_period, ratio_ref_period = get_period_inputs(first_df_len)

    # Compute volatility & ratios
    final_df = compute_multiple_volatility_ratios(
        selected_symbols, files, data_folder, custom_period, ratio_ref_period
    )

    # Add clickable stock links
    final_df["Stock"] = final_df["Symbol"].apply(
        lambda s: f"/Stocks?symbol={urllib.parse.quote(s)}"
    )

    # Reorder columns: Symbol first, then Stock, then others
    cols = ["Symbol", "Stock"] + \
        [c for c in final_df.columns if c not in ["Symbol", "Stock"]]
    final_df = final_df[cols]

    st.subheader("Volatility & Ratios Table")
    st.data_editor(
        final_df,
        column_config={
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
        },
        hide_index=True,
        key="compare_stocks_editor"
    )


if __name__ == "__main__":
    compare_stocks_view()
