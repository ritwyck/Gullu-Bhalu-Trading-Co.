import os
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from Brain.volatility import load_data, realized_volatility, historical_volatility, volatility_ratio


def compare_stocks_view():
    st.header("📊 Multiple Stock Volatility Comparison")

    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    selected_symbols = st.multiselect(
        "Select 2-5 stocks", symbols, default=symbols[:2])
    if not (2 <= len(selected_symbols) <= 5):
        st.warning("Please select 2 to 5 stocks.")
        return

    fixed_periods = [5, 10, 15, 30, 60]
    vol_table_data = []
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        for p in fixed_periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                vol_table_data.append({"Symbol": sym, "Period (days)": p,
                                      "Historical Volatility (Annualized %)": annual_vol * 100})

    st.subheader("Historical Volatility Table (All Stocks)")
    vol_table_df = pd.DataFrame(vol_table_data)
    st.dataframe(vol_table_df)

    # Primary analysis period
    period = st.radio("Select primary volatility period",
                      fixed_periods + ["Custom"])
    if period == "Custom":
        period = st.number_input(
            "Custom primary period", min_value=2, max_value=365, value=10)

    results = []
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        rv = realized_volatility(df.tail(period)["Close"])
        _, hv_annual = historical_volatility(df.tail(period)["Close"])
        results.append({"Symbol": sym, "Realized Volatility (%)": rv *
                       100, "Historical Volatility (Annualized %)": hv_annual * 100})

    comp_df = pd.DataFrame(results)
    st.subheader(f"Volatility Comparison Table ({period}-day)")
    st.dataframe(comp_df)

    # Select second vol for ratio
    ratio_ref = st.radio("Select reference volatility (%)", options=[100] + sorted(
        vol_table_df["Historical Volatility (Annualized %)"].unique().round(2).tolist()))
    ratio_results = []
    for sym in selected_symbols:
        hv_annual = comp_df.loc[comp_df["Symbol"] == sym,
                                "Historical Volatility (Annualized %)"].values[0]
        ratio_results.append(
            {"Symbol": sym, "Volatility Ratio (%)": volatility_ratio(hv_annual, ratio_ref)})

    ratio_df = pd.DataFrame(ratio_results)
    st.subheader(f"Volatility Ratio Table (ref={ratio_ref}%)")
    st.dataframe(ratio_df)

    # Plot
    metric = st.radio("Select metric to plot", [
                      "Open", "High", "Low", "Close", "Volatility"])
    window = 10
    if metric == "Volatility":
        window = st.number_input(
            "Volatility rolling window", min_value=2, max_value=100, value=10)

    dfs = []
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
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
        x="Date:T", y="Value:Q", color="Symbol:N", tooltip=["Date:T", "Symbol:N", "Value:Q"]
    ).properties(width=700, height=400, title=f"{metric} Comparison")
    st.altair_chart(chart, use_container_width=True)
