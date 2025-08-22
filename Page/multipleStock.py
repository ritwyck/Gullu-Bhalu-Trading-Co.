import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data, _get_live, _get_symbols_from_query, _set_symbols_in_query
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


def render_multi_stocks(symbols: list[str]):
    valid_data = {}
    for sym in symbols:
        df = _get_live(sym)
        if df is not None and not df.empty:
            valid_data[sym] = df
        else:
            st.warning(f"No live historical data found for {sym}. Skipping.")

    if not valid_data:
        st.error("No valid data available for selected symbols.")
        return

    # === Show last 30 days OHLC for each stock ===
    st.subheader("📊 Recent OHLC Data")
    for sym, df in valid_data.items():
        recent_df = df.tail(30)
        ohlc_cols = [c for c in ["Open", "High",
                                 "Low", "Close"] if c in df.columns]
        if not recent_df.empty and ohlc_cols:
            st.markdown(f"**{sym}**")
            st.dataframe(recent_df.loc[:, ohlc_cols])
        else:
            st.info(f"No OHLC data available for {sym}.")

    # === Combined price chart ===
    st.subheader("📈 Price Comparison")
    import plotly.graph_objects as go
    fig = go.Figure()
    for sym, df in valid_data.items():
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name=sym
        ))
    fig.update_layout(xaxis_title="Date",
                      yaxis_title="Close Price", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # === Volatility & Ratio table ===
    max_len = max(len(df) for df in valid_data.values())
    fixed_periods, ratio_ref_period = get_period_inputs(max_len)

    all_vol_rows = []
    for sym, df in valid_data.items():
        vol_rows = compute_volatility_and_ratios(
            df, fixed_periods, ratio_ref_period)
        for row in vol_rows:
            row["Symbol"] = sym
            all_vol_rows.append(row)

    if all_vol_rows:
        st.subheader("📊 Volatility & Ratio Table")
        vol_df = pd.DataFrame(all_vol_rows)
        st.dataframe(vol_df)
    else:
        st.info("Volatility & ratio calculations unavailable.")

    # === ADX table ===
    all_adx_rows = []
    for sym, df in valid_data.items():
        adx_rows = compute_adx_table(df, fixed_periods)
        for row in adx_rows:
            row["Symbol"] = sym
            all_adx_rows.append(row)

    if all_adx_rows:
        st.subheader("📊 ADX Table")
        adx_df = pd.DataFrame(all_adx_rows)
        st.dataframe(adx_df)
    else:
        st.info("ADX calculations unavailable.")
