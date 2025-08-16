import os
import pandas as pd
import streamlit as st
import urllib.parse
from Backend.Strategy.volatility import load_data, historical_volatility
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from Frontend.modules.page_config import set_page_config

set_page_config()

hide_default_nav()  # Hide the default multipage nav
selected_page = custom_sidebar()


def all_stocks_view():
    st.header("All Stock Volatility & Ratios")
    # Your existing implementation here...


if selected_page == "Home":
    st.markdown("<h1 style='color:#04B4D9;'>Welcome to Trade Jockey</h1>",
                unsafe_allow_html=True)
    st.markdown("Use the sidebar to navigate.")
elif selected_page == "All Stocks":
    all_stocks_view()
elif selected_page == "Compare Stocks":
    from pages import Compare_Stocks
    Compare_Stocks.compare_stocks_view()
elif selected_page == "Individual Stocks":
    from pages import Individual_Stocks
    Individual_Stocks.single_stock_view()
else:
    st.write("Please select a page from the sidebar.")


if selected_page == "Home":
    st.markdown("<h1 style='text-align:center; color:#04B4D9;'>Trade Jockey Dashboard</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "### Welcome! Analyze stocks with powerful volatility analytics.")

    st.markdown("---")

    st.markdown("## 📌 Available Pages")
    st.markdown("""
    - **All Stocks Overview**: Quick selection & comparison of multiple stocks  
    - **Compare Stocks**: Compare selected stocks side by side  
    - **Individual Stocks**: Deep dive into any single stock
    """)

    st.markdown("---")
    st.info(
        "Use the sidebar to navigate. Select stocks and compare with a single click!")

elif selected_page == "All Stocks":
    from pages import All_Stocks
    All_Stocks.all_stocks_view()

elif selected_page == "Compare Stocks":
    from pages import Compare_Stocks
    Compare_Stocks.compare_stocks_view()

elif selected_page == "Individual Stocks":
    from pages import Individual_Stocks
    Individual_Stocks.single_stock_view()
