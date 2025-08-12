import os
import pandas as pd
import streamlit as st
from Brain.volatility import load_data, realized_volatility, historical_volatility, volatility_ratio
from FrontEnd.plot import plot_stock_metric


def single_stock_view():
    st.header("📈 Single Stock Volatility Analysis")

    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    symbol = st.selectbox("Select stock symbol", symbols)
    file_match = [f for f in files if f.startswith(symbol)][0]
    df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

    # Table of volatilities for multiple periods
    fixed_periods = [5, 10, 15, 30, 60]
    vol_data = []
    for p in fixed_periods:
        if p <= len(df):
            _, annual_vol = historical_volatility(df.tail(p)["Close"])
            vol_data.append(
                {"Period (days)": p, "Historical Volatility (Annualized %)": annual_vol * 100})

    custom_period = st.number_input(
        "Custom period (days)", min_value=2, max_value=len(df), value=10)
    _, custom_annual_vol = historical_volatility(
        df.tail(custom_period)["Close"])
    vol_data.append({"Period (days)": custom_period,
                    "Historical Volatility (Annualized %)": custom_annual_vol * 100})

    st.subheader(f"{symbol} Historical Volatility Table")
    vol_table_df = pd.DataFrame(vol_data)
    st.dataframe(vol_table_df)

    # Primary volatility period
    period = st.radio("Select primary period for analysis",
                      fixed_periods + ["Custom"])
    if period == "Custom":
        period = st.number_input(
            "Custom primary period", min_value=2, max_value=len(df), value=10)

    rv = realized_volatility(df.tail(period)["Close"])
    hv, hv_annual = historical_volatility(df.tail(period)["Close"])

    summary_df = pd.DataFrame([
        {"Metric": "Realized Volatility (%)", f"{period}-day Value": rv * 100},
        {"Metric": "Historical Volatility (Annualized %)",
         f"{period}-day Value": hv_annual * 100}
    ])
    st.subheader(f"{symbol} Volatility Summary")
    st.dataframe(summary_df)

    # Second volatility for ratio
    ratio_ref = st.radio("Select second volatility reference (%)", options=[
                         100] + [round(v["Historical Volatility (Annualized %)"], 2) for v in vol_data])
    ratio = volatility_ratio(hv_annual * 100, ratio_ref)

    ratio_df = pd.DataFrame(
        [{"Metric": f"Volatility Ratio (ref={ratio_ref}%)", f"{period}-day Value": ratio}])
    st.subheader(f"{symbol} Volatility Ratio")
    st.dataframe(ratio_df)

    # Plot metric
    metric = st.radio("Select metric to plot", [
                      "Open", "High", "Low", "Close", "Volatility"])
    window = 10
    if metric == "Volatility":
        window = st.number_input(
            "Volatility rolling window", min_value=2, max_value=100, value=10)
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)
