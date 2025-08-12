
from Brain.volatility import realized_volatility, load_data, historical_volatility, volatility_ratio
from FrontEnd.plot import plot_stock_metric
import numpy as np
import sys
import os
import pandas as pd
import streamlit as st
import altair as alt


# --- Main App ---
st.title("Stock Volatility & Comparison")

files = [f for f in os.listdir(
    "Vault/Historical_Stock_Data") if f.endswith(".csv")]
symbols = [os.path.splitext(f)[0] for f in files]  # removes '.csv'

compare_mode = st.checkbox("Compare multiple stocks")

if not compare_mode:
    # SINGLE STOCK VIEW
    symbol = st.selectbox("Select stock symbol", symbols, key="single_symbol")
    file_match = [f for f in files if f.startswith(symbol)][0]
    df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

    period = st.radio("Select volatility period", options=[
                      5, 10, 15, 30, 60, "Custom"], key="single_period")
    if period == "Custom":
        period = st.number_input("Enter custom period (days)", min_value=2, max_value=len(
            df), value=10, key="single_custom_period")

    rv = realized_volatility(df.tail(period)["Close"])
    hv, hv_annual = historical_volatility(df.tail(period)["Close"])

    # Volatility summary table
    summary_data = [{
        "Metric": "Realized Volatility (%)",
        f"{period}-day Value": rv * 100
    }, {
        "Metric": "Historical Volatility (Annualized %)",
        f"{period}-day Value": hv_annual * 100
    }]
    summary_df = pd.DataFrame(summary_data)
    st.subheader(f"{symbol} Volatility Summary")
    st.dataframe(summary_df)

    # Calculate volatility ratio using your imported function
    # Default second volatility is 100 as per your function
    ratio = volatility_ratio(hv_annual * 100)

    ratio_data = [{
        "Metric": "Volatility Ratio (%)",
        f"{period}-day Value": ratio
    }]
    ratio_df = pd.DataFrame(ratio_data)
    st.subheader(f"{symbol} Volatility Ratio")
    st.dataframe(ratio_df)

    # Now select metric to plot
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

        # Calculate volatility and prepare summary and ratio tables
        results = []
        ratio_results = []

        for sym in selected_symbols:
            file_match = [f for f in files if f.startswith(sym)][0]
            df = load_data(os.path.join(
                "Vault/Historical_Stock_Data", file_match))

            rv = realized_volatility(df.tail(period)["Close"])
            hv, hv_annual = historical_volatility(df.tail(period)["Close"])

            results.append({
                "Symbol": sym,
                "Realized Volatility (%)": rv * 100,
                "Historical Volatility (Annualized %)": hv_annual * 100
            })

            # Calculate volatility ratio using historical volatility annualized
            # assumes second vol defaults to 100
            ratio = volatility_ratio(hv_annual * 100)

            ratio_results.append({
                "Symbol": sym,
                "Volatility Ratio (%)": ratio
            })

        # Display volatility summary table
        comp_df = pd.DataFrame(results)
        st.subheader("Volatility Comparison Table")
        st.dataframe(comp_df)

        # Display volatility ratio table below volatility summary
        ratio_df = pd.DataFrame(ratio_results)
        st.subheader("Volatility Ratio Table")
        st.dataframe(ratio_df)

        # Now let user select metric and window for plotting
        metric = st.radio("Select metric to plot", options=[
                          "Open", "High", "Low", "Close", "Volatility"], key="compare_metric")
        window = 10
        if metric == "Volatility":
            window = st.number_input("Volatility rolling window", min_value=2,
                                     max_value=100, value=10, key="compare_vol_window")

        dfs = []
        for sym in selected_symbols:
            file_match = [f for f in files if f.startswith(sym)][0]
            df = load_data(os.path.join(
                "Vault/Historical_Stock_Data", file_match))
            if metric == "Volatility":
                df["Volatility"] = df["Close"].rolling(
                    window).std() * np.sqrt(window)
            col_name = metric if metric != "Volatility" else "Volatility"
            df_plot = df[["Date", col_name]].copy()
            df_plot["Symbol"] = sym
            df_plot.rename(columns={col_name: "Value"}, inplace=True)
            dfs.append(df_plot)

        combined_df = pd.concat(dfs)
        chart = alt.Chart(combined_df).mark_line().encode(
            x="Date:T",
            y=alt.Y("Value:Q", title=metric),
            color="Symbol:N",
            tooltip=["Date:T", "Symbol:N", "Value:Q"]
        ).properties(width=700, height=400, title=f"{metric} Comparison")
        st.altair_chart(chart, use_container_width=True)
