import streamlit as st
import os
import pandas as pd
import numpy as np
import altair as alt


def realized_volatility(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.std()


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    # Only clean Close if it's string/object type
    if df["Close"].dtype == object:
        df["Close"] = df["Close"].str.replace(",", "").astype(float)
    return df


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


# --- Main App ---
st.title("Stock Volatility & Comparison")

files = [f for f in os.listdir("HistoricalData") if f.endswith(".csv")]
symbols = [os.path.splitext(f)[0] for f in files]  # removes '.csv'

compare_mode = st.checkbox("Compare multiple stocks")

if not compare_mode:
    # SINGLE STOCK VIEW
    symbol = st.selectbox("Select stock symbol", symbols, key="single_symbol")
    file_match = [f for f in files if f.startswith(symbol)][0]
    df = load_data(os.path.join("HistoricalData", file_match))

    period = st.radio("Select volatility period", options=[
                      5, 10, 15, 30, 60, "Custom"], key="single_period")
    if period == "Custom":
        period = st.number_input("Enter custom period (days)", min_value=2, max_value=len(
            df), value=10, key="single_custom_period")

    vol = realized_volatility(df.tail(period)["Close"])
    st.write(
        f"**{period}-day Volatility:** {vol:.4f} (decimal), {vol*100:.2f}%")

    metric = st.radio("Select metric to plot", options=[
                      "Open", "High", "Low", "Close", "Volatility"], key="single_metric")
    window = 10
    if metric == "Volatility":
        window = st.number_input("Volatility rolling window", min_value=2,
                                 max_value=100, value=10, key="single_vol_window")
    plot_stock_metric(df, metric, window if metric == "Volatility" else None)

else:
    # COMPARE MULTIPLE STOCKS
    selected_symbols = st.multiselect(
        "Select 2 to 5 stocks to compare", symbols, default=symbols[:2], key="compare_symbols")
    if len(selected_symbols) < 2:
        st.warning("Select at least 2 stocks to compare.")
    elif len(selected_symbols) > 5:
        st.warning("Select up to 5 stocks.")
    else:
        period = st.radio("Select volatility period", options=[
                          5, 10, 15, 30, 60, "Custom"], key="compare_period")
        if period == "Custom":
            period = st.number_input("Enter custom period (days)", min_value=2,
                                     max_value=365, value=10, key="compare_custom_period")

        data = []
        for sym in selected_symbols:
            file_match = [f for f in files if f.startswith(sym)][0]
            df = load_data(os.path.join("HistoricalData", file_match))
            vol = realized_volatility(df.tail(period)["Close"])
            data.append({"Symbol": sym, f"{period}-day Volatility (decimal)": vol,
                        f"{period}-day Volatility (%)": vol*100})

        comp_df = pd.DataFrame(data)
        st.dataframe(comp_df)

        # Plot comparison of volatility bars
        bar_chart = alt.Chart(comp_df).mark_bar().encode(
            x=alt.X(f"{period}-day Volatility (%)", title="Volatility (%)"),
            y=alt.Y('Symbol', sort='-x', title='Stock Symbol'),
            color='Symbol'
        ).properties(title=f"Volatility Comparison over {period} days")

        st.altair_chart(bar_chart, use_container_width=True)
