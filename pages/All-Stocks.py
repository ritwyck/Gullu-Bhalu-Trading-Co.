import os
import pandas as pd
import streamlit as st
import urllib.parse
from Backend.Strategy.volatility import load_data, historical_volatility
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from Frontend.modules.page_config import set_page_config

set_page_config()

hide_default_nav()  # Hide the default multipage nav
selected_page = custom_sidebar()


def all_stocks_view():
    st.header("All Stock Volatility & Ratios")

    # Load CSV files
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    custom_period = st.number_input(
        "Select Volatility period in days", 2, 365, 10, key="compare_custom_vol_period")
    ratio_ref_period = st.number_input(
        "Select Ratio period in days", 2, 365, 5, step=1, key="compare_ratio_ref_period")

    fixed_periods = [5, 10, 30, 100]
    rows = []

    for sym in symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        periods = sorted(set(fixed_periods + [custom_period]))
        row_fields = {}

        ref_vol = None
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])

        for p in periods:
            if p <= len(df):
                _, ann = historical_volatility(df.tail(p)["Close"])
                row_fields[f"Vol_{p}d"] = round(ann, 3)
                row_fields[f"Ratio_{p}d"] = round(
                    ann / ref_vol, 3) if (ref_vol and ref_vol != 0) else pd.NA

        stock_url = f"/Stocks?symbol={urllib.parse.quote(sym)}"
        row = {"Symbol": sym, "Stock": stock_url, **row_fields}
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Compare"] = False  # checkbox column

    st.subheader("Volatility & Ratios Table")
    edited = st.data_editor(
        df,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Compare": st.column_config.CheckboxColumn("Compare"),
        },
        hide_index=True,
        key="stock_compare_editor",
    )

    selected = edited.loc[edited["Compare"], "Symbol"].tolist()

    if selected:
        encoded = urllib.parse.quote(",".join(selected))
        compare_url = f"/Compare-Stocks?symbols={encoded}"

        st.markdown(
            f"""
            <a href="{compare_url}">
                <button style="
                    background-color:#4CAF50;
                    border:none;
                    color:white;
                    padding:10px 20px;
                    text-align:center;
                    text-decoration:none;
                    display:inline-block;
                    font-size:16px;
                    border-radius:8px;
                    cursor:pointer;
                ">
                🔗 Compare Selected Stocks
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    all_stocks_view()
