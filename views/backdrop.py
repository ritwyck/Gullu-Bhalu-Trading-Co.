import streamlit as st
import requests
import yfinance as yf
from datetime import datetime, timedelta
from UserInterface.modules.symbol_search import get_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data


def render_backdrop():
    st.title("Trade Jockey Dashboard")
    query = st.text_input("Search Company Symbol")

    if query:
        symbols = get_symbols(query)
        if symbols:
            st.write("Matching companies and symbols:")
            for symbol, description in symbols:
                # Render a clickable button for each symbol
                if st.button(f"{symbol} — {description}"):
                    with st.spinner(f"Fetching historical data for {symbol}..."):
                        hist = fetch_historical_data(symbol)
                        if hist.empty:
                            st.write(
                                "No historical data found for the last week.")
                        else:
                            st.write(
                                f"Last week historical data for {symbol}:")
                            st.dataframe(hist)
                            st.line_chart(hist['Close'])
        else:
            st.write("No matches found.")


if __name__ == "__main__":
    render_backdrop()
