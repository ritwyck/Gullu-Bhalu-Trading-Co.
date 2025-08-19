import streamlit as st
import requests
import yfinance as yf
from datetime import datetime, timedelta

FINNHUB_KEY = "d2i2vppr01qucbnmsn7gd2i2vppr01qucbnmsn80"


def get_symbols(query):
    url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_KEY}"
    data = requests.get(url).json()
    matches = data.get("result", [])[:5]
    return [(m.get("symbol", ""), m.get("description", "")) for m in matches]


def fetch_historical_data(symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_date.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    return hist


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
