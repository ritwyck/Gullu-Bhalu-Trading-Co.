import streamlit as st
from FrontEnd.singleStockView import single_stock_view
from FrontEnd.multiStockView import compare_stocks_view

st.title("📊 Stock Volatility Dashboard")

mode = st.radio("Choose Mode", ["Single Stock", "Compare Multiple Stocks"])

if mode == "Single Stock":
    single_stock_view()
else:
    compare_stocks_view()
