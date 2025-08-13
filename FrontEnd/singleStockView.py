import os
import pandas as pd
import streamlit as st
from Brain.volatility import load_data, realized_volatility, historical_volatility
from FrontEnd.plot import plot_stock_metric


def single_stock_view():
    st.header("Single Stock Volatility Analysis")

    # Load available stocks
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # Select stock symbol
    symbol = st.selectbox("Select stock symbol", symbols)
    file_match = [f for f in files if f.startswith(symbol)][0]
    df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

    # Metric plotting controls
    metric = st.radio("Select metric",
                      ["Open", "High", "Low", "Close", "Volatility"],
                      key="single_metric")
    window = 10
    if metric == "Volatility":
        window = st.number_input("Volatility rolling window",
                                 min_value=2, max_value=100, value=10,
                                 key="single_vol_window")
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    # Volatility table for fixed periods
    fixed_periods = [5, 10, 15, 30, 60]
    vol_data = []
    for p in fixed_periods:
        if p <= len(df):
            _, annual_vol = historical_volatility(df.tail(p)["Close"])
            vol_data.append({
                "Period": p,
                "Historical Volatility": annual_vol * 100  # consistent column name
            })

    # Add custom period volatility
    custom_period = st.number_input("Select Volatility period in days",
                                    min_value=2, max_value=len(df), value=10,
                                    key="custom_vol_period")
    _, custom_vol = historical_volatility(df.tail(custom_period)["Close"])
    vol_data.append({
        "Period": custom_period,
        "Historical Volatility": custom_vol * 100  # same column name as above
    })

    # Create volatility DataFrame, sort by period
    vol_table_df = pd.DataFrame(vol_data).sort_values(
        "Period").reset_index(drop=True)

    # Select reference period for ratio
    ratio_ref_period = st.number_input("Select Ratio period in days",
                                       min_value=2, max_value=len(df),
                                       value=5, step=1, key="ratio_ref_period")

    # Calculate reference historical volatility for ratio
    _, ref_vol = historical_volatility(df.tail(ratio_ref_period)["Close"])

    # Add ratio column (ratio of each period to chosen reference period)
    if ref_vol != 0:
        ratio_col_name = f"Ratio vs {ratio_ref_period}-day Historical Volatility"
        vol_table_df[ratio_col_name] = (
            vol_table_df["Historical Volatility"] / (ref_vol * 100)
        ) * 100
    else:
        ratio_col_name = f"Ratio vs {ratio_ref_period}-day Historical Volatility"
        vol_table_df[ratio_col_name] = pd.NA

    # Display the combined volatility and ratio table
    st.subheader(f"{symbol} Historical Volatility Table")
    st.dataframe(vol_table_df)
