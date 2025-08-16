from Frontend.modules.page_config import set_page_config
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from views.home import render_home
from views.all_stocks import render_all_stocks
from views.compare import render_compare_stocks
from views.single import render_single_stock
import streamlit as st
import os
import pandas as pd
from Backend.Strategy.volatility import load_data, historical_volatility
from Frontend.modules.plot import plot_stock_metric
from Frontend.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from Frontend.modules.ui_controls import get_metric_and_window, get_period_inputs
from Frontend.modules.calculations import compute_volatility_and_ratios, compute_adx_table, compute_multiple_volatility_ratios
import urllib.parse
from Frontend.modules.data_loading import load_symbol_data, get_stock_files, get_symbols

set_page_config()
hide_default_nav()
page = custom_sidebar()

routes = {
    "Home": render_home,
    "All-Stocks": render_all_stocks,
    "Compare-Stocks": render_compare_stocks,
    "Stocks": render_single_stock,
}

routes.get(page, lambda: st.error("Page not found"))()
