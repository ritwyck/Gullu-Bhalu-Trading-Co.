import streamlit as st
from FrontEnd.singleStockView import single_stock_view
from FrontEnd.multiStockView import compare_stocks_view
from FrontEnd.allStockView import all_stocks_view

st.title("📊 Stock Volatility Dashboard")

mode = st.radio("Choose Mode", ["Single Stock",
                "Compare Stocks", "All Stocks"])

if mode == "Single Stock":
    single_stock_view()
elif mode == "Compare Stocks":  # match exact string from the options above
    compare_stocks_view()
else:  # This will trigger if "All Stocks" is selected
    all_stocks_view()
