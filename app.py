import streamlit as st
import os
import pandas as pd
import numpy as np
import altair as alt


def realized_volatility(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.std()


def rolling_volatility(prices, window=10):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.rolling(window=window).std()


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


st.title("Stock Volatility Calculator & Chart")

# Load files
files = [f for f in os.listdir("HistoricalData") if f.endswith(".csv")]
symbols = [f.split("_")[0] for f in files]

symbol = st.selectbox("Select stock symbol", options=symbols)
file_match = [f for f in files if f.startswith(symbol)][0]
df = load_data(os.path.join("HistoricalData", file_match))

# Volatility calculation section
st.subheader("Volatility Calculation")

period_option = st.radio("Select period", options=[
                         "10 days", "30 days", "Custom"])
if period_option == "Custom":
    period = st.number_input("Enter number of days",
                             min_value=2, max_value=len(df), value=10)
elif period_option == "10 days":
    period = 10
else:
    period = 30

vol = realized_volatility(df.tail(period)["Close"])
st.write(f"**{period}-day Volatility:** {vol:.4f} (decimal), {vol*100:.2f}%")

# Metric plotting section
st.subheader("Performance Chart")

metric = st.radio("Select metric to plot", options=[
                  "Open", "High", "Low", "Close", "Volatility"])

if metric == "Volatility":
    window = st.number_input(
        "Volatility rolling window for chart", min_value=2, max_value=100, value=10)
    df["Volatility"] = rolling_volatility(df["Close"], window=window)
    plot_df = df[["Date", "Volatility"]].dropna()
    ylabel = f"Rolling {window}-day Volatility"
    y_col = "Volatility"
else:
    plot_df = df[["Date", metric]]
    ylabel = metric
    y_col = metric

chart = (
    alt.Chart(plot_df)
    .mark_line()
    .encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y(f'{y_col}:Q', title=ylabel)
    )
    .properties(
        width=700,
        height=400,
        title=f"{ylabel}/Time for {symbol}"
    )
)

st.altair_chart(chart, use_container_width=True)
