import urllib.parse
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def render_single_stock():
    """Render the single stock analysis page with search and live data only."""

    st.title("📈 Trade Jockey Dashboard")

    # --- Search input for company name or symbol ---
    query = st.text_input("🔎 Search company name or symbol")

    selected_symbol = None

    if query:
        matches = search_symbols(query)  # List of (symbol, description)
        if matches:
            st.write("Matching companies and symbols:")
            for symbol, description in matches:
                if st.button(f"{symbol} — {description}"):
                    selected_symbol = symbol
                    # Clear other buttons by breaking loop
                    break
        else:
            st.warning("No matches found.")

    # --- Require symbol selection via search ---
    if selected_symbol is None:
        st.info("Please search and select a company symbol above to proceed.")
        return

    # --- Update URL param for selected symbol ---
    st.query_params["symbol"] = selected_symbol

    # --- Fetch live historical data for selected symbol ---
    df_live = fetch_historical_data(selected_symbol)

    if df_live is None or df_live.empty:
        st.error(
            f"No live historical data found for symbol '{selected_symbol}'.")
        return

    # --- Show OHLC last week table from live data ---
    if not isinstance(df_live.index, pd.DatetimeIndex):
        df_live.index = pd.to_datetime(df_live.index)

    start_date = datetime.today() - timedelta(days=7)
    last_week_df = df_live[df_live.index >= start_date]

    if not last_week_df.empty:
        st.subheader(f"{selected_symbol} - Last Week OHLC Data")
        st.dataframe(last_week_df.loc[:, ["Open", "High", "Low", "Close"]])
        st.line_chart(last_week_df["Close"])
    else:
        st.info("No recent last week data available.")

    # --- Use live data for plotting and calculations ---
    df = df_live

    # --- Plot metric and volatility ---
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

    # --- Compute volatility, ratios, and ADX ---
    fixed_periods, ratio_ref_period = get_period_inputs(len(df))
    vol_rows = compute_volatility_and_ratios(
        df, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df, fixed_periods)

    # --- Display tables ---
    st.subheader(f"{selected_symbol} - Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))

    st.subheader(f"{selected_symbol} - ADX Table")
    st.dataframe(pd.DataFrame(adx_rows))


if __name__ == "__main__":
    render_single_stock()
