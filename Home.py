import os
import pandas as pd
import streamlit as st
import urllib.parse
from Backend.Strategy.volatility import load_data, historical_volatility
from Frontend.modules.sidebar import custom_sidebar, hide_default_nav
from Frontend.modules.page_config import set_page_config
from Frontend.modules.plot import plot_stock_metric
from Frontend.modules.data_loading import get_stock_files, get_symbols, load_symbol_data
from Frontend.modules.ui_controls import get_metric_and_window, get_period_inputs
from Frontend.modules.calculations import compute_volatility_and_ratios, compute_adx_table, compute_multiple_volatility_ratios
import urllib.parse
from Frontend.modules.data_loading import load_symbol_data, get_stock_files, get_symbols

set_page_config()
hide_default_nav()

selected_page = custom_sidebar()


def home_view():
    st.markdown("<h1 style='color:#04B4D9;'>Welcome to Trade Jockey Dashboard</h1>",
                unsafe_allow_html=True)
    st.write("Use the sidebar to explore different analytics.")


def all_stocks_view():
    st.header("All Stock Volatility & Ratios")

    # Load CSV files
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    custom_period = st.number_input(
        "Select Volatility period in days", 2, 365, 10, key="compare_custom_vol_period")
    ratio_ref_period = st.number_input(
        "Select Ratio period in days", 2, 365, 5, step=1, key="compare_ratio_ref_period")

    fixed_periods = [5, 10, 30, 100]
    rows = []

    for sym in symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        periods = sorted(set(fixed_periods + [custom_period]))
        row_fields = {}

        ref_vol = None
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])

        for p in periods:
            if p <= len(df):
                _, ann = historical_volatility(df.tail(p)["Close"])
                row_fields[f"Vol_{p}d"] = round(ann, 3)
                row_fields[f"Ratio_{p}d"] = round(
                    ann / ref_vol, 3) if (ref_vol and ref_vol != 0) else pd.NA

        stock_url = f"/Stocks?symbol={urllib.parse.quote(sym)}"
        row = {"Symbol": sym, "Stock": stock_url, **row_fields}
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Compare"] = False  # checkbox column

    st.subheader("Volatility & Ratios Table")
    edited = st.data_editor(
        df,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Compare": st.column_config.CheckboxColumn("Compare"),
        },
        hide_index=True,
        key="stock_compare_editor",
    )

    selected = edited.loc[edited["Compare"], "Symbol"].tolist()

    if selected:
        encoded = urllib.parse.quote(",".join(selected))
        compare_url = f"/Compare-Stocks?symbols={encoded}"

        st.markdown(
            f"""
            <a href="{compare_url}">
                <button style="
                    background-color:#4CAF50;
                    border:none;
                    color:white;
                    padding:10px 20px;
                    text-align:center;
                    text-decoration:none;
                    display:inline-block;
                    font-size:16px;
                    border-radius:8px;
                    cursor:pointer;
                ">
                🔗 Compare Selected Stocks
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )


def compare_stocks_view():
    st.header("Multiple Stock Volatility Comparison")

    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    all_symbols = get_symbols(files)

    params = st.query_params
    selected_symbols = None

    # Initialize from URL params or default to first 2 symbols
    if "symbols" in params:
        param_syms = params["symbols"]
        if isinstance(param_syms, list):
            selected_symbols = param_syms[0].split(",")
        else:
            selected_symbols = param_syms.split(",")
    else:
        selected_symbols = all_symbols[:2]

    # Multiselect
    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare",
        all_symbols,
        default=selected_symbols,
        help="Select at least 2 and up to 10 stocks"
    )

    # 🚨 Enforce minimum of 2
    if len(selected_symbols) < 2:
        st.warning("You must keep at least 2 stocks selected. Resetting...")
        selected_symbols = all_symbols[:2]  # reset
        st.experimental_rerun()

    # Update query params
    st.query_params["symbols"] = ",".join(selected_symbols)

    st.query_params["symbols"] = ",".join(selected_symbols)

    # Get user period inputs
    first_df_len = len(load_symbol_data(
        data_folder, selected_symbols[0], files))
    custom_period, ratio_ref_period = get_period_inputs(first_df_len)

    # Compute volatility & ratios
    final_df = compute_multiple_volatility_ratios(
        selected_symbols, files, data_folder, custom_period, ratio_ref_period
    )

    # Add clickable stock links
    final_df["Stock"] = final_df["Symbol"].apply(
        lambda s: f"/Stocks?symbol={urllib.parse.quote(s)}"
    )

    # Reorder columns: Symbol first, then Stock, then others
    cols = ["Symbol", "Stock"] + \
        [c for c in final_df.columns if c not in ["Symbol", "Stock"]]
    final_df = final_df[cols]

    st.subheader("Volatility & Ratios Table")
    st.data_editor(
        final_df,
        column_config={
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
        },
        hide_index=True,
        key="compare_stocks_editor"
    )


def single_stock_view():
    st.header("Single Stock - Volatility, Ratio & ADX")

    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    symbols = get_symbols(files)

    # Robust way to extract default symbol from query params
    params = st.query_params
    # If param exists, use it; else first symbol.
    default_symbol = params.get("symbol", symbols[0])
    # If the param is passed as a list like ['TATASTEEL']
    if isinstance(default_symbol, list):
        default_symbol = default_symbol

    symbol = st.selectbox(
        "Select stock symbol",
        symbols,
        index=symbols.index(default_symbol) if default_symbol in symbols else 0
    )

    # Update URL when user changes selection
    st.query_params["symbol"] = symbol

    df = load_symbol_data(data_folder, symbol, files)
    if df is None:
        st.error(f"No data found for symbol '{symbol}'.")
        return

    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    fixed_periods, ratio_ref_period = get_period_inputs(len(df))

    vol_rows = compute_volatility_and_ratios(
        df, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df, fixed_periods)

    st.subheader(f"{symbol} - Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))

    st.subheader(f"{symbol} - ADX Table (TradingView/Yahoo Style)")
    st.dataframe(pd.DataFrame(adx_rows))


# Routing logic: Only ONE function runs each render!
if selected_page == "Home":
    home_view()
elif selected_page == "All-Stocks":
    all_stocks_view()
elif selected_page == "Compare-Stocks":
    compare_stocks_view()
elif selected_page == "Stocks":
    single_stock_view()
else:
    st.error("Page not found.")
