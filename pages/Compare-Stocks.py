import os
import streamlit as st
import altair as alt
import pandas as pd
from Frontend.modules.data_loading import load_symbol_data, get_stock_files, get_symbols
from Frontend.modules.ui_controls import get_metric_and_window, get_period_inputs
from Frontend.modules.calculations import compute_multiple_volatility_ratios


def compare_stocks_view(selected_symbols=None):
    st.header("Multiple Stock Volatility Comparison")

    data_folder = "Vault/Historical_Stock_Data"
    files = get_stock_files(data_folder)
    all_symbols = get_symbols(files)

    # Use query params for initial selection if available
    params = st.query_params
    if selected_symbols is None:
        # Read from query params if present, else default
        if "symbols" in params:
            param_syms = params["symbols"]
            # params["symbols"] may be a comma-separated string or list
            if isinstance(param_syms, list):
                selected_symbols = param_syms[0].split(",")
            else:
                selected_symbols = param_syms.split(",")
        else:
            selected_symbols = all_symbols[:2]

    # Let user update selection via multiselect
    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare",
        all_symbols,
        default=selected_symbols,
        help="Select at least 2 and up to 10 stocks"
    )

    # Update query params on selection change
    st.query_params["symbols"] = ",".join(selected_symbols)

    # Validate selection
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
        df = load_symbol_data(data_folder, sym, files)
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

    # Plot with Altair
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

    # Get inputs for tables, using length of the first selected symbol's data
    df_first = load_symbol_data(data_folder, selected_symbols[0], files)
    custom_period, ratio_ref_period = get_period_inputs(len(df_first))

    final_df = compute_multiple_volatility_ratios(
        selected_symbols, files, data_folder, custom_period, ratio_ref_period
    )

    # Convert symbols to clickable Markdown links
    base_single_stock_url = "/Stocks?symbol="
    final_df["Symbol"] = final_df["Symbol"].apply(
        lambda sym: f"[{sym}]({base_single_stock_url}{sym})"
    )

    st.subheader("Volatility & Ratios")
    st.markdown(final_df.to_markdown(index=False), unsafe_allow_html=True)


if __name__ == "__main__":
    compare_stocks_view()
