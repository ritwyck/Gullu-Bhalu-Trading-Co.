import os
import pandas as pd
import streamlit as st
import urllib.parse
from Backend.Strategy.volatility import load_data, historical_volatility


def all_stocks_view():
    st.header("All Stock Volatility & Ratios")

    # Load CSV files
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2,
        max_value=365,
        value=10,
        key="compare_custom_vol_period",
    )
    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2,
        max_value=365,
        value=5,
        step=1,
        key="compare_ratio_ref_period",
    )

    fixed_periods = [5, 10, 30, 100]
    vol_rows = []

    # Build table rows
    for sym in symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        periods = sorted(set(fixed_periods + [custom_period]))
        row_data_vol = {}

        ref_vol = None
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])

        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data_vol[f"Vol_{p}d"] = round(annual_vol, 3)
                row_data_vol[f"Ratio_{p}d"] = (
                    round(annual_vol / ref_vol,
                          3) if (ref_vol and ref_vol != 0) else pd.NA
                )

        # Stock link (for markdown rendering)
        base_single_stock_url = "/Stocks?symbol="
        row_data_vol = {
            "Stock": f"[{sym}]({base_single_stock_url}{urllib.parse.quote(sym)})",
            "Symbol": sym,  # raw symbol for compare
            **row_data_vol
        }

        vol_rows.append(row_data_vol)

    vol_df = pd.DataFrame(vol_rows)

    # --- Selection column ---
    vol_df["Compare"] = False

    edited_df = st.data_editor(
        vol_df,
        column_config={
            "Compare": st.column_config.CheckboxColumn("Compare"),
            # shows markdown text
            "Stock": st.column_config.TextColumn("Stock", disabled=True),
        },
        hide_index=True,
        key="stock_compare_editor"
    )

    # Selected symbols
    selected_symbols = edited_df.loc[edited_df["Compare"], "Symbol"].tolist()

    if selected_symbols:
        encoded = urllib.parse.quote(",".join(selected_symbols))
        compare_url = f"/Compare-Stocks?symbols={encoded}"
        st.markdown(f"[Compare Selected Stocks]({compare_url})")

    # Render pretty table with clickable links
    display_df = edited_df.drop(columns=["Compare", "Symbol"])
    st.subheader("Volatility & Ratios Table")
    st.markdown(display_df.to_markdown(index=False), unsafe_allow_html=True)


if __name__ == "__main__":
    all_stocks_view()
