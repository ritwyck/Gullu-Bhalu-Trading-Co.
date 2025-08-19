import streamlit as st
import os
import pandas as pd
import numpy as np
import altair as alt

from Logic.Strategy.volatility import realized_volatility


def plot_stock_metric(df, metric, window=None):
    if metric == "Volatility":
        vol = df["Close"].rolling(window).apply(
            lambda x: realized_volatility(x), raw=False)
        plot_df = df[["Date"]].copy()
        plot_df["Volatility"] = vol
        y_col = "Volatility"
        ylabel = f"Rolling {window}-day Volatility"
    else:
        plot_df = df[["Date", metric]].copy()
        y_col = metric
        ylabel = metric

    chart = (
        alt.Chart(plot_df.dropna())
        .mark_line()
        .encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y(f'{y_col}:Q', title=ylabel)
        )
        .properties(width=700, height=400, title=f"{ylabel} over Time")
    )
    st.altair_chart(chart, use_container_width=True)
