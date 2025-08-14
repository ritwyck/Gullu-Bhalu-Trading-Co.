import os
import pandas as pd
import streamlit as st
from Brain.Strategy.volatility import load_data, historical_volatility


def all_stocks_view():
    st.header("All Stock Volatility Comparison")

    # Fetch ALL available stock symbols
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]
    selected_symbols = symbols  # all stocks in the DB

    # === Controls (custom and ratio period)
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

    fixed_periods = [5, 10, 15, 30, 60, 200]
    all_rows = []

    # Loop over each symbol
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

        # Build list of periods to calculate
        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        # this row will hold all metrics for one stock
        row_data = {"Symbol": sym}

        # Calculate reference vol for ratio
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        # For each period, add historical vol & ratio
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data[f"Vol_{p}d"] = annual_vol  # decimal value
                if ref_vol and ref_vol != 0:
                    row_data[f"Ratio_{p}d_vs_{ratio_ref_period}d"] = annual_vol / ref_vol
                else:
                    row_data[f"Ratio_{p}d_vs_{ratio_ref_period}d"] = pd.NA

        all_rows.append(row_data)

    # Convert to DataFrame, 1 row per stock
    final_df = pd.DataFrame(all_rows)

    st.subheader(f"All Stocks")
    st.dataframe(final_df)
