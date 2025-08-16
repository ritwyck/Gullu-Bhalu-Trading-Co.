import os
import pandas as pd
import streamlit as st
from Backend.Strategy.volatility import load_data, historical_volatility


def all_stocks_view():
    st.header("All Stock Volatility, Ratios & ADX Comparison")

    # Load CSV files
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # User inputs
    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2, max_value=365, value=10,
        key="compare_custom_vol_period"
    )

    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2, max_value=365, value=5,
        step=1,
        key="compare_ratio_ref_period"
    )

    fixed_periods = [5, 10, 30, 100]
    vol_rows = []

    # Build table rows with volatility and ratios data
    for sym in symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        periods = sorted(set(fixed_periods + [custom_period]))
        row_data_vol = {"Symbol": sym}

        # Reference volatility for ratios
        ref_vol = None
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])

        # Fill in volatility and ratios
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data_vol[f"Vol_{p}d"] = round(annual_vol, 3)
                row_data_vol[f"Ratio_{p}d"] = round(
                    annual_vol / ref_vol, 3) if (ref_vol and ref_vol != 0) else pd.NA

        vol_rows.append(row_data_vol)

    vol_df = pd.DataFrame(vol_rows)

    # Initialize or load selected symbols set from session state
    if "selected_symbols" not in st.session_state:
        st.session_state.selected_symbols = set()

    # Add a Compare checkbox column, initial values based on session state
    vol_df["Compare"] = vol_df["Symbol"].apply(
        lambda s: s in st.session_state.selected_symbols)

    # Convert Symbol column to markdown links to single stock view for display only
    base_single_stock_url = "/SingleStockView?symbol="
    vol_df["Symbol_Display"] = vol_df["Symbol"].apply(
        lambda sym: f"[{sym}]({base_single_stock_url}{sym})")

    # Reorder columns to show Symbol_Display first and hide original Symbol in display
    display_cols = ["Symbol_Display"] + [c for c in vol_df.columns if c not in [
        "Symbol", "Symbol_Display", "Compare"]] + ["Compare"]

    st.subheader("Volatility & Ratios Table with Selection")
    edited_df = st.data_editor(
        vol_df[display_cols],
        column_config={
            "Compare": st.column_config.CheckboxColumn("Compare")
        },
        hide_index=True,
        use_container_width=True
    )

    # Update session state with latest selections from edited_df
    # Map back the symbol names from Symbol_Display markdown links by stripping markdown format
    def extract_symbol(markdown_link):
        # markdown is like [SYM](url), extract SYM
        if markdown_link.startswith("[") and "](" in markdown_link:
            return markdown_link.split("](")[0][1:]
        return markdown_link

    st.session_state.selected_symbols = set(
        edited_df.loc[edited_df["Compare"],
                      "Symbol_Display"].apply(extract_symbol)
    )

    if st.button("Compare Selected Stocks"):
        if st.session_state.selected_symbols:
            selected_list = ",".join(st.session_state.selected_symbols)
            st.experimental_set_query_params(symbols=selected_list)
            st.experimental_rerun()  # trigger page change or reload
            # Alternatively, use st.switch_page if Streamlit multipage setup
            # st.switch_page("pages/multiStockView.py")
        else:
            st.warning("Select at least one stock to compare.")
