import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


# ----------------------------
# Caching wrapper for live data
# ----------------------------
@st.cache_data(ttl=0, show_spinner=False)
def _get_live(symbol: str) -> pd.DataFrame | None:
    try:
        df = fetch_historical_data(symbol, period="2y", interval="1d")
        if df is None or df.empty:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].copy()
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert(None)
        return df.sort_index()
    except Exception:
        return None


# ----------------------------
# Query Param Helpers
# ----------------------------
def _get_symbols_from_query() -> list[str]:
    qp = st.query_params
    val = qp.get("symbol")
    if isinstance(val, str):
        return [val]
    elif isinstance(val, list):
        return val
    else:
        return []


def _set_symbols_in_query(symbols: list[str]) -> None:
    st.query_params["symbol"] = symbols


# ----------------------------
# Single Stock Renderer
# ----------------------------
def render_single_stock(symbol: str):
    df_live = _get_live(symbol)
    if df_live is None or df_live.empty:
        st.error(f"No live historical data found for '{symbol}'.")
        return

    # Raw OHLC display
    recent_df = df_live.tail(30)
    ohlc_cols = [c for c in ["Open", "High",
                             "Low", "Close"] if c in df_live.columns]
    if not recent_df.empty and ohlc_cols:
        st.subheader(f"{symbol} Data")
        st.dataframe(recent_df.loc[:, ohlc_cols])
    else:
        st.info("No OHLC data available.")

    # Metric selection and chart
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    df_for_plot = df_live.reset_index().rename(columns={"index": "Date"})
    plot_stock_metric(df_for_plot, metric, window if metric ==
                      "Volatility" else None)

    # Volatility & Ratio / ADX tables
    fixed_periods, ratio_ref_period = get_period_inputs(len(df_live))
    vol_rows = compute_volatility_and_ratios(
        df_live, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df_live, fixed_periods)

    if vol_rows:
        st.subheader(f"{symbol} — Volatility & Ratio Table")
        st.dataframe(pd.DataFrame(vol_rows))
    else:
        st.info("Volatility & ratio calculations unavailable for this symbol.")

    if adx_rows:
        st.subheader(f"{symbol} — ADX Table")
        st.dataframe(pd.DataFrame(adx_rows))
    else:
        st.info("ADX calculations unavailable for this symbol.")


# ----------------------------
# Compare Stocks Renderer
# ----------------------------
def render_compare_stocks(symbols: list[str]):
    st.title("📊 Trade Jockey Dashboard - Compare Stocks")
    valid_data = {}
    for sym in symbols:
        df = _get_live(sym)
        if df is not None and not df.empty:
            valid_data[sym] = df
        else:
            st.warning(f"No live data found for {sym}. Skipping.")

    if not valid_data:
        st.error("No valid data found for any selected stocks.")
        return

    max_len = max(len(df) for df in valid_data.values())
    fixed_periods, ratio_ref_period = get_period_inputs(max_len)

    all_rows = []
    for sym, df in valid_data.items():
        vol_rows = compute_volatility_and_ratios(
            df, fixed_periods, ratio_ref_period)
        for row in vol_rows:
            row["Symbol"] = sym
            all_rows.append(row)

    if not all_rows:
        st.error("Volatility & ratio calculations unavailable for selected symbols.")
        return

    vol_df = pd.DataFrame(all_rows)
    st.subheader("Volatility & Ratio Comparison Table")
    st.dataframe(vol_df)

    # Plot each stock
    for sym, df in valid_data.items():
        st.markdown(f"### {sym} - Close Price Chart")
        df_for_plot = df.reset_index().rename(columns={"index": "Date"})
        plot_stock_metric(df_for_plot, "Close", None)


# ----------------------------
# Main Entry
# ----------------------------
def main():
    st.set_page_config(page_title="Trade Jockey Dashboard", layout="wide")
    mode = st.sidebar.radio("Select mode", ["Single Stock", "Compare Stocks"])
    symbols = _get_symbols_from_query()

    if mode == "Single Stock":
        st.title("📈 Trade Jockey Dashboard - Single Stock")
        symbol = symbols[0] if symbols else "AAPL"

        search_query = st.text_input(
            "🔎 Search company name or symbol", key="search_text_single")
        if search_query:
            matches = search_symbols(search_query)
            if matches:
                st.write("Matching companies and symbols:")
                for sym, desc in matches:
                    if st.button(f"{sym} — {desc}", key=f"btn_single_{sym}"):
                        _set_symbols_in_query([sym])
                        st.rerun()
            else:
                st.warning("No matches found.")

        render_single_stock(symbol)

    else:  # Compare Stocks mode
        st.title("📊 Trade Jockey Dashboard - Compare Stocks")

        default_compare = ["AAPL", "MSFT"]
        selected_symbols = symbols if len(symbols) >= 2 else default_compare

        search_query = st.text_input(
            "🔎 Search company names or symbols (comma separated)",
            key="search_text_compare"
        )

        matched_symbols_set = set()
        if search_query:
            terms = [t.strip() for t in search_query.split(",") if t.strip()]
            for term in terms:
                matches = search_symbols(term)
                for sym, _ in matches:
                    matched_symbols_set.add(sym)

        matched_symbols = sorted(matched_symbols_set)

        if matched_symbols:
            selected_symbols = st.multiselect(
                "Select 2 to 10 stocks to compare from matched symbols",
                matched_symbols,
                default=selected_symbols,
                help="Select at least 2 and up to 10 stocks",
            )
            _set_symbols_in_query(selected_symbols)

        # Guard clause: wait for 2+ valid symbols
        if not selected_symbols or len(selected_symbols) < 2:
            st.info("Please select at least 2 company symbols above to compare.")
            return

        # Limit to 10 stocks
        if len(selected_symbols) > 10:
            st.warning("Please select no more than 10 stocks.")
            selected_symbols = selected_symbols[:10]
            _set_symbols_in_query(selected_symbols)

        # === Fetch & Plot ===
        valid_data = {}
        for sym in selected_symbols:
            df = _get_live(sym)
            if df is not None and not df.empty:
                valid_data[sym] = df
            else:
                st.warning(f"No data for {sym}, skipping.")

        if not valid_data:
            st.error("No valid data found for selected stocks.")
            return

        # Combine into one chart
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

        # Volatility & Ratios
        max_len = max(len(df) for df in valid_data.values())
        fixed_periods, ratio_ref_period = get_period_inputs(max_len)

        all_rows = []
        for sym, df in valid_data.items():
            vol_rows = compute_volatility_and_ratios(
                df, fixed_periods, ratio_ref_period)
            for row in vol_rows:
                row["Symbol"] = sym
                all_rows.append(row)

        if all_rows:
            st.subheader("📊 Volatility & Ratio Comparison")
            st.dataframe(pd.DataFrame(all_rows))
        else:
            st.info("Volatility & ratio calculations unavailable.")

            render_compare_stocks(selected_symbols)


if __name__ == "__main__":
    main()
