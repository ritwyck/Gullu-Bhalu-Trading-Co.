import os
import streamlit as st
import altair as alt
import pandas as pd
from Frontend.modules.data_loading import load_symbol_data

from Frontend.modules.data_loading import get_stock_files, get_symbols
from Frontend.modules.ui_controls import select_symbols, get_metric_and_window, get_period_inputs
from Frontend.modules.calculations import compute_multiple_volatility_ratios
from Frontend.modules.plot import plot_stock_metric


def compare_stocks_view(selected_symbols=None):
    st.header("Multiple Stock Volatility Comparison")

    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    all_symbols = [os.path.splitext(f)[0] for f in files]

    # Provide default selected_symbols (first 2 symbols) if None or <2 selected
    if selected_symbols is None or len(selected_symbols) < 2:
        selected_symbols = all_symbols[:2]

    # Allow user to update stock selection via multiselect
    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare",
        all_symbols,
        default=selected_symbols,
        help="Select at least 2 and up to 10 stocks"
    )

    # Validate selected_symbols length
    if len(selected_symbols) < 2:
        st.warning("Please select at least 2 stocks to compare.")
        return
    if len(selected_symbols) > 10:
        st.warning("Select up to 10 stocks only.")
        return

    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "compare_metric"
    )

    # Build combined dataframe for plotting
    dfs_plot = []
    for sym in selected_symbols:
        df = load_symbol_data(data_folder, sym, files)  # sym is a string!
        if df is None:
            st.warning(f"No data found for symbol '{sym}'. Skipping.")
            continue
        if metric == "Volatility":
            df["Volatility"] = df["Close"].rolling(
                window).std() * (window ** 0.5)
            col_name = "Volatility"
        else:
            col_name = metric
        df_plot = df[["Date", col_name]].copy()
        df_plot["Symbol"] = sym
        df_plot.rename(columns={col_name: "Value"}, inplace=True)
        dfs_plot.append(df_plot)

    if not dfs_plot:
        st.error("No valid stock data available for plotting.")
        return

    combined_df_plot = pd.concat(dfs_plot)

    chart = (
        alt.Chart(combined_df_plot)
        .mark_line()
        .encode(
            x="Date:T",
            y=alt.Y("Value:Q", title=metric),
            color="Symbol:N",
            tooltip=["Date:T", "Symbol:N", "Value:Q"],
        )
        .properties(width=700, height=400, title=f"{metric} Comparison over Time")
    )

    st.altair_chart(chart, use_container_width=True)

    # Get length of first selected symbol's data for period inputs
    df_first = load_symbol_data(data_folder, selected_symbols[0], files)
    custom_period, ratio_ref_period = get_period_inputs(len(df_first))

    final_df = compute_multiple_volatility_ratios(
        selected_symbols, files, data_folder, custom_period, ratio_ref_period
    )

    # Convert symbols to clickable Markdown links
    base_single_stock_url = "/SingleStockView?symbol="
    final_df["Symbol"] = final_df["Symbol"].apply(
        lambda sym: f"[{sym}]({base_single_stock_url}{sym})"
    )

    st.subheader("Volatility & Ratios")
    st.markdown(final_df.to_markdown(index=False), unsafe_allow_html=True)
