from UserInterface.modules.page_config import set_page_config
from UserInterface.modules.sidebar import custom_sidebar, hide_default_nav
from views.all_stocks import render_all_stocks
from views.single import render_single_stock
from Logic.Strategy.volatility import load_data, historical_volatility
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table, compute_multiple_volatility_ratios
import urllib.parse
from UserInterface.modules.data_loading import load_symbol_data, get_stock_files, get_symbols
import streamlit as st
import os
import pandas as pd

set_page_config()
hide_default_nav()
page = custom_sidebar()


routes = {
    "Stocks": render_single_stock,
    "All-Stocks": render_all_stocks
}

routes.get(page, lambda: st.error("Page not found"))()
