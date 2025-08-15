import os
import pandas as pd
import streamlit as st
from Brain.Strategy.volatility import load_data, historical_volatility
from Brain.Strategy.adx import calculate_adx


def all_stocks_view():
    st.header("All Stock Volatility, Ratios & ADX Comparison")

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
    vol_rows = []
    adx_rows = []

    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        row_data_vol = {"Symbol": sym}
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data_vol[f"Volatility_{p}d"] = annual_vol
                if ref_vol and ref_vol != 0:
                    row_data_vol[f"Ratio_{p}d"] = annual_vol / ref_vol
                else:
                    row_data_vol[f"Ratio_{p}d"] = pd.NA

        vol_rows.append(row_data_vol)

    # --- VOLATILITY TABLE ---
    vol_df = pd.DataFrame(vol_rows)
    vol_df = vol_df.round(3)

    st.subheader("Volatility & Ratios Table")
    st.dataframe(vol_df)
