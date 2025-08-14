import os
import pandas as pd
import streamlit as st
from Brain.Strategy.volatility import load_data, realized_volatility, historical_volatility
import altair as alt


def compare_stocks_view():
    st.header("Multiple Stock Volatility Comparison")

    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # Select 2 to 5 stocks
    selected_symbols = st.multiselect(
        "Select 2 to 5 stocks to compare", symbols, default=symbols[:2]
    )
    if len(selected_symbols) < 2:
        st.warning("Please select at least 2 stocks to compare.")
        return
    if len(selected_symbols) > 5:
        st.warning("Select up to 5 stocks only.")
        return

    # --- Metric plotting controls ---
    metric = st.radio(
        "Select metric", ["Open", "High", "Low", "Close", "Volatility"], key="compare_metric"
    )
    window = 10
    if metric == "Volatility":
        window = st.number_input(
            "Volatility rolling window",
            min_value=2,
            max_value=100,
            value=10,
            key="compare_vol_window",
        )

    # Plotting
    dfs_plot = []
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        if metric == "Volatility":
            df["Volatility"] = df["Close"].rolling(
                window).std() * (window ** 0.5)
        col_name = metric if metric != "Volatility" else "Volatility"
        df_plot = df[["Date", col_name]].copy()
        df_plot["Symbol"] = sym
        df_plot.rename(columns={col_name: "Value"}, inplace=True)
        dfs_plot.append(df_plot)

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

    # === Historical Vol Table ===
    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2,
        max_value=365,
        value=10,
        key="compare_custom_vol_period",
    )

    fixed_periods = [5, 10, 15, 30, 60, 100]
    all_vol_data = []

    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                all_vol_data.append({
                    "Symbol": sym,
                    "Period": p,
                    # Store as decimal, not percentage
                    "Historical Volatility": annual_vol
                })

    combined_vol_df = pd.DataFrame(all_vol_data)

    hist_vol_pivot = combined_vol_df.pivot_table(
        index="Period", columns="Symbol", values="Historical Volatility"
    ).sort_index()

    st.subheader("Historical Volatility (Decimal)")
    st.dataframe(hist_vol_pivot)

    # === Ratio Table ===
    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2,
        max_value=365,
        value=5,
        step=1,
        key="compare_ratio_ref_period",
    )

    ratio_vol_data = []

    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        stock_df = combined_vol_df[combined_vol_df["Symbol"] == sym].copy()

        if ref_vol and ref_vol != 0:
            stock_df[f"Ratio vs {ratio_ref_period}-day"] = (
                stock_df["Historical Volatility"] / ref_vol
            )
        else:
            stock_df[f"Ratio vs {ratio_ref_period}-day"] = pd.NA

        ratio_vol_data.append(stock_df)

    combined_ratio_df = pd.concat(ratio_vol_data)

    ratio_col_name = f"Ratio vs {ratio_ref_period}-day"
    ratio_pivot = combined_ratio_df.pivot_table(
        index="Period", columns="Symbol", values=ratio_col_name
    ).sort_index()

    st.subheader(
        f"Volatility Ratios Relative to {ratio_ref_period}-day (Decimal)")
    st.dataframe(ratio_pivot)
