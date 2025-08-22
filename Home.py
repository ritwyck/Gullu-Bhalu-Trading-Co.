import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data, _get_live, _get_symbols_from_query, _set_symbols_in_query
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table
from Page.singleStock import render_single_stock


def main():
    st.set_page_config(page_title="Trade Jockey Dashboard", layout="wide")
    mode = st.sidebar.radio("Select mode", ["Single Stock", "Compare Stocks"])
    symbols = _get_symbols_from_query()

    if mode == "Single Stock":
        st.title("📈 Trade Jockey Dashboard")
        symbol = symbols[0] if symbols else "AAPL"

        search_query = st.text_input(
            "🔎 Search company name or symbol", key="search_text_single")
        if search_query:
            matches = search_symbols(search_query)
            if matches:
                st.write("Matching companies and symbols:")
                for sym, desc in matches:
                    if st.button(f"{sym} — {desc}", key=f"btn_single_{sym}"):
                        _set_symbols_in_query([sym])
                        st.rerun()
            else:
                st.warning("No matches found.")

        render_single_stock(symbol)


if __name__ == "__main__":
    main()
