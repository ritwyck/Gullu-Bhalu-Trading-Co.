import streamlit as st
import os
from volatility import realized_volatility, load_data

st.title("Stock Volatility Calculator")

# List CSV files in HistoricalData folder
files = [f for f in os.listdir("HistoricalData") if f.endswith(".csv")]

# Symbol selector
symbol = st.selectbox("Select stock symbol", options=[
                      f.replace(".csv", "") for f in files])

# Load selected file
df = load_data(symbol)

# Period selection
period_option = st.radio("Select period", options=[
                         "10 days", "30 days", "Custom"])

if period_option == "Custom":
    period = st.number_input("Enter number of days",
                             min_value=2, max_value=len(df), value=10)
elif period_option == "10 days":
    period = 10
else:
    period = 30

# Calculate volatility
vol = realized_volatility(df.tail(period)["Close"])

st.write(f"**{period}-day Volatility:** {vol:.4f} (decimal), {vol*100:.2f}%")
