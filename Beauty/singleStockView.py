import os
import pandas as pd
import streamlit as st
import numpy as np
from Brain.Strategy.volatility import realized_volatility, load_data, historical_volatility, volatility_ratio
from Brain.Strategy.adx import calculate_adx

from Beauty.plot import plot_stock_metric


def single_stock_view():
    st.header("Single Stock - Volatility, Ratio & ADX")

    # Load available stocks
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # Select stock symbol
    symbol = st.selectbox("Select stock symbol", symbols)
    file_match = [f for f in files if f.startswith(symbol)][0]
    df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

    # Metric plotting controls
    metric = st.radio("Select metric to plot", [
                      "Open", "High", "Low", "Close", "Volatility"], key="single_metric")
    window = 10
    if metric == "Volatility":
        window = st.number_input("Volatility rolling window", min_value=2,
                                 max_value=100, value=10, key="single_vol_window")
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    # Period inputs
    fixed_periods = [5, 10, 15, 30, 60, 100]
    custom_period = st.number_input("Select Volatility period in days", min_value=2, max_value=len(
        df), value=10, key="custom_vol_period")
    if custom_period not in fixed_periods:
        fixed_periods.append(custom_period)
    fixed_periods = sorted(fixed_periods)

    ratio_ref_period = st.number_input("Select Ratio period in days", min_value=2, max_value=len(
        df), value=5, step=1, key="ratio_ref_period")

    # Reference volatility
    _, ref_vol = historical_volatility(df["Close"].tail(ratio_ref_period))

    # Compute ADX on the full dataset
    adx_period = 14  # standard ADX period
    plus_di_series, minus_di_series, adx_series = calculate_adx(
        df["High"].values, df["Low"].values, df["Close"].values, period=adx_period)

    vol_rows, adx_rows = [], []

    for p in fixed_periods:
        annual_vol = ratio_val = None
        plus_di_val = minus_di_val = adx_val = None

        # Volatility
        if p <= len(df):
            _, annual_vol = historical_volatility(df["Close"].tail(p))
            if ref_vol and ref_vol != 0:
                ratio_val = annual_vol / ref_vol

        # ADX values (pick last value in slice ending at period p)
        plus_di_series, minus_di_series, adx_series = None, None, None
        if p >= adx_period:
            df_slice = df.tail(p)
            adx_df = calculate_adx(df_slice["High"].values,
                                   df_slice["Low"].values,
                                   df_slice["Close"].values,
                                   period=adx_period)
            plus_di_val = round(
                adx_df["+DI"].iloc[-1], 1) if not np.isnan(adx_df["+DI"].iloc[-1]) else None
            minus_di_val = round(
                adx_df["-DI"].iloc[-1], 1) if not np.isnan(adx_df["-DI"].iloc[-1]) else None
            adx_val = round(
                adx_df["ADX"].iloc[-1], 1) if not np.isnan(adx_df["ADX"].iloc[-1]) else None

        vol_rows.append({
            "Volatility Period": p,
            "Historical Volatility": round(annual_vol, 3) if annual_vol is not None else None,
            f"Ratio vs {ratio_ref_period}d": round(ratio_val, 3) if ratio_val is not None else None,
        })

        adx_rows.append({
            "Period": p,
            "+DI": plus_di_val,
            "-DI": minus_di_val,
            "ADX": adx_val,
        })

    st.subheader(f"{symbol} - Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))

    st.subheader(f"{symbol} - ADX Table (TradingView/Yahoo Style)")
    st.dataframe(pd.DataFrame(adx_rows))
