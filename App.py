
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

    # Volatility periods to display in the table
    fixed_periods = [5, 10, 15, 30, 60]

    # Calculate volatilities for fixed periods plus custom if selected
    vol_data = []
    all_periods = fixed_periods.copy()

    for p in fixed_periods:
        if p <= len(df):
            _, annual_vol = historical_volatility(df.tail(p)["Close"])
            vol_data.append({
                "Period (days)": p,
                "Historical Volatility (Annualized %)": annual_vol * 100
            })
    # Custom period input for displaying volatility in the table
    custom_period = st.number_input("Enter custom period (days) for volatility table",
                                    min_value=2, max_value=len(df), value=10, key="single_custom_table_period")
    all_periods.append(custom_period)
    _, custom_annual_vol = historical_volatility(
        df.tail(custom_period)["Close"])
    vol_data.append({
        "Period (days)": custom_period,
        "Historical Volatility (Annualized %)": custom_annual_vol * 100
    })

    vol_table_df = pd.DataFrame(vol_data).sort_values("Period (days)")
    st.subheader(f"{symbol} Historical Volatility Table")
    st.dataframe(vol_table_df)

    # Primary volatility period selection (for plotting and main volatility display)
    period = st.radio("Select volatility period to view main volatility", options=[
                      *fixed_periods, "Custom"], index=0, key="single_period")
    if period == "Custom":
        period = st.number_input("Enter custom period (days) for main volatility",
                                 min_value=2, max_value=len(df), value=10, key="single_custom_period")

    # Calculate volatilities for the primary period
    rv = realized_volatility(df.tail(period)["Close"])
    hv, hv_annual = historical_volatility(df.tail(period)["Close"])

    # Display main volatility summary
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

    # Second volatility period selection for ratio using radio with options + Custom
    ratio_options = [100]  # Default 100 as baseline for ratio
    # Add the historical volatilities from the table for selection
    ratio_option_dict = {"100": 100.0}
    for row in vol_data:
        key = str(row["Period (days)"])
        ratio_options.append(key)
        ratio_option_dict[key] = row["Historical Volatility (Annualized %)"]

    ratio_choice = st.radio("Select second volatility for ratio",
                            options=ratio_options, index=0, key="single_second_vol_ratio")

    # If user selects custom numeric input for ratio besides 100 and fixed periods
    if ratio_choice == "100":
        second_vol = 100.0
    else:
        second_vol = ratio_option_dict[ratio_choice]

    # Calculate ratio based on main period volatility and selected second volatility
    ratio = volatility_ratio(hv_annual * 100, second_vol)

    ratio_data = [{
        "Metric": f"Volatility Ratio (ref={ratio_choice}) (%)",
        f"{period}-day Value": ratio
    }]
    ratio_df = pd.DataFrame(ratio_data)
    st.subheader(f"{symbol} Volatility Ratio")
    st.dataframe(ratio_df)

    # Metric selection and plotting (unchanged)
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
        fixed_periods = [5, 10, 15, 30, 60]

        period = st.radio(
            "Select volatility period", options=[*fixed_periods, "Custom"], key="compare_period")
        if period == "Custom":
            period = st.number_input(
                "Enter custom period (days)", min_value=2, max_value=365, value=10, key="compare_custom_period")

        # Prepare volatility table data for all selected stocks
        vol_table_data = []
        all_periods = fixed_periods.copy()

        # For efficiency, calculate volatilities per period once per stock
        vol_per_stock = {}
        for sym in selected_symbols:
            file_match = [f for f in files if f.startswith(sym)][0]
            df = load_data(os.path.join(
                "Vault/Historical_Stock_Data", file_match))
            vol_per_stock[sym] = {}
            for p in fixed_periods:
                if p <= len(df):
                    _, annual_vol = historical_volatility(df.tail(p)["Close"])
                    vol_per_stock[sym][p] = annual_vol * 100  # percentage
                    vol_table_data.append({
                        "Symbol": sym,
                        "Period (days)": p,
                        "Historical Volatility (Annualized %)": annual_vol * 100
                    })
            # Handle custom period volatility
            if period == "Custom" and period not in fixed_periods and period <= len(df):
                _, annual_vol_custom = historical_volatility(
                    df.tail(period)["Close"])
                vol_per_stock[sym][period] = annual_vol_custom * 100
                vol_table_data.append({
                    "Symbol": sym,
                    "Period (days)": period,
                    "Historical Volatility (Annualized %)": annual_vol_custom * 100
                })

        vol_table_df = pd.DataFrame(vol_table_data)
        st.subheader("Volatility Table for Selected Stocks")
        st.dataframe(vol_table_df)

        # Flatten all unique volatilities from table for ratio selection options
        unique_vols = sorted(
            set(vol_table_df["Historical Volatility (Annualized %)"].unique()))

        # Provide options including default 100 and custom input
        ratio_options = ["100"]
        ratio_options.extend([f"{v:.2f}" for v in unique_vols])

        selected_ratio_str = st.radio(
            "Select second volatility for ratio", options=ratio_options, index=0, key="compare_ratio_vol")
        if selected_ratio_str == "100":
            second_vol = 100.0
        else:
            second_vol = float(selected_ratio_str)

        # Now calculate key volatilities and ratios for each selected stock
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

            ratio_val = volatility_ratio(hv_annual * 100, second_vol)
            ratio_results.append({
                "Symbol": sym,
                "Volatility Ratio (%)": ratio_val
            })

        # Display volatility summary table
        comp_df = pd.DataFrame(results)
        st.subheader(f"Volatility Comparison Table ({period}-day)")
        st.dataframe(comp_df)

        # Display volatility ratio table
        ratio_df = pd.DataFrame(ratio_results)
        st.subheader(
            f"Volatility Ratio Table (Ref volatility: {second_vol:.2f}%)")
        st.dataframe(ratio_df)

        # Metric selection and plotting
        metric = st.radio("Select metric to plot", options=[
                          "Open", "High", "Low", "Close", "Volatility"], key="compare_metric")
        window = 10
        if metric == "Volatility":
            window = st.number_input(
                "Volatility rolling window", min_value=2, max_value=100, value=10, key="compare_vol_window")

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
