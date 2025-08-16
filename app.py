from Frontend.modules.page_config import set_page_config
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from views.home import render_home
from views.all_stocks import render_all_stocks
from views.compare import render_compare_stocks
from views.single import render_single_stock
import streamlit as st

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
