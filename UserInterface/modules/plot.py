import streamlit as st
import os
import pandas as pd
import numpy as np
import altair as alt

from Logic.Strategy.volatility import realized_volatility


def plot_stock_metric(df: pd.DataFrame, metric: str, window: int | None = None):
    """Plots either a chosen metric or rolling volatility from a stock DataFrame."""

    # Ensure we always have a 'Date' column
    if "Date" not in df.columns:
        df = df.reset_index().rename(
            columns={df.index.name or "index": "Date"})

    if metric == "Volatility" and window:
        # Example: compute rolling volatility
        df["Volatility"] = df["Close"].pct_change().rolling(window).std()
        y_col = "Volatility"
        ylabel = f"Rolling {window}-day Volatility"
    else:
        if metric not in df.columns:
            st.error(f"Metric '{metric}' not found in data.")
            return
        y_col = metric
        ylabel = metric

    plot_df = df[["Date", y_col]].dropna()

    if plot_df.empty:
        st.warning(f"No data available to plot for {metric}.")
        return

    st.line_chart(
        plot_df.set_index("Date")[y_col],
        use_container_width=True,
        height=400,
    )
    st.caption(f"Chart: {ylabel}")
