import os
import pandas as pd
import streamlit as st
from Brain.Strategy.volatility import load_data, historical_volatility
import altair as alt


def compare_stocks_view():
    st.header("Multiple Stock Volatility Comparison")

    # === Load available symbols ===
    files = [f for f in os.listdir(
        "Vault/Historical_Stock_Data") if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # === Let user select 2–5 stock symbols ===
    selected_symbols = st.multiselect(
        "Select 2 to 10 stocks to compare", symbols, default=symbols[:2]
    )
    if len(selected_symbols) < 2:
        st.warning("Please select at least 2 stocks to compare.")
        return
    if len(selected_symbols) > 10:
        st.warning("Select up to 10 stocks only.")
        return

    # === Metric plotting controls ===
    metric = st.radio(
        "Select metric", ["Open", "High", "Low", "Close", "Volatility"], key="compare_metric"
    )
    window = 10
    if metric == "Volatility":
        window = st.number_input(
            "Volatility rolling window",
            min_value=2, max_value=100, value=10,
            key="compare_vol_window",
        )

    # === Plot selected metric for all selected stocks ===
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

    # === Volatility table inputs ===
    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2, max_value=365, value=10,
        key="compare_custom_vol_period",
    )
    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2, max_value=365, value=5,
        step=1,
        key="compare_ratio_ref_period",
    )

    fixed_periods = [5, 10, 30, 100]
    all_rows = []

    # === Build wide-format table: 1 row per stock ===
    for sym in selected_symbols:
        file_match = [f for f in files if f.startswith(sym)][0]
        df = load_data(os.path.join("Vault/Historical_Stock_Data", file_match))

        # Periods to calculate
        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        row_data = {"Symbol": sym}

        # Reference volatility for ratios
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        # Fill row with all vols then ratios
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data[f"Volatility_{p}d"] = annual_vol
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data[f"Ratio_{p}d"] = (
                    annual_vol / ref_vol) if (ref_vol and ref_vol != 0) else pd.NA

        all_rows.append(row_data)

    final_df = pd.DataFrame(all_rows)

    # === Column ordering: Symbol, all vols, spacer, all ratios ===
    cols = list(final_df.columns)
    vol_cols = [c for c in cols if c.startswith("Volatility_")]
    ratio_cols = [c for c in cols if c.startswith("Ratio_")]

    barrier_col = "-----"  # visual barrier column
    final_df[barrier_col] = ""

    ordered_cols = ["Symbol"] + vol_cols + [barrier_col] + ratio_cols
    final_df = final_df[ordered_cols]

    st.subheader("Volatility & Ratios")
    st.dataframe(final_df)
