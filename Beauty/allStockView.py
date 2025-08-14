import os
import pandas as pd
import streamlit as st
from Brain.Strategy.volatility import load_data, historical_volatility


def all_stocks_view():
    st.header("All Stock Volatility and Ratio Comparison")

    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]
    selected_symbols = symbols

    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2, max_value=365, value=10,
        key="compare_custom_vol_period"
    )
    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2, max_value=365, value=5, step=1,
        key="compare_ratio_ref_period"
    )

    fixed_periods = [5, 10, 30, 100]
    all_rows = []

    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        row_data = {"Symbol": sym}

        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data[f"Volatility_{p}d"] = annual_vol
                if ref_vol and ref_vol != 0:
                    row_data[f"Ratio_{p}d"] = annual_vol / ref_vol
                else:
                    row_data[f"Ratio_{p}d"] = pd.NA

        all_rows.append(row_data)

    final_df = pd.DataFrame(all_rows)

    cols = list(final_df.columns)
    vol_cols = [col for col in cols if col.startswith("Volatility_")]
    ratio_cols = [col for col in cols if col.startswith("Ratio_")]

    barrier_col = "-----"
    final_df[barrier_col] = ""  # empty column as barrier

    ordered_cols = ["Symbol"] + vol_cols + [barrier_col] + ratio_cols
    final_df = final_df[ordered_cols]

    st.dataframe(final_df)
