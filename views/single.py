import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


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
    st.experimental_set_query_params(symbol=symbols)


def render_single_stock(symbol: str):
    st.title("📈 Trade Jockey Dashboard - Single Stock")

    df_live = _get_live(symbol)
    if df_live is None or df_live.empty:
        st.error(f"No live historical data found for '{symbol}'.")
        return

    recent_df = df_live.tail(30)
    ohlc_cols = [c for c in ["Open", "High",
                             "Low", "Close"] if c in df_live.columns]
    if not recent_df.empty and ohlc_cols:
        st.subheader(f"{symbol} Data")
        st.dataframe(recent_df.loc[:, ohlc_cols])
    else:
        st.info("No OHLC data available.")

    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    df_for_plot = df_live.reset_index().rename(columns={"index": "Date"})
    plot_stock_metric(df_for_plot, metric, window if metric ==
                      "Volatility" else None)

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


def render_compare_stocks(symbols: list[str]):
    st.title("📊 Trade Jockey Dashboard - Compare Stocks")

    # Fetch data for all symbols
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

    # Plot individual close price charts
    for sym, df in valid_data.items():
        st.markdown(f"### {sym} - Close Price Chart")
        df_for_plot = df.reset_index().rename(columns={"index": "Date"})
        plot_stock_metric(df_for_plot, "Close", None)


def main():
    mode = st.sidebar.radio("Select mode", ["Single Stock", "Compare Stocks"])
    symbols = _get_symbols_from_query()

    if mode == "Single Stock":
        symbol = symbols[0] if symbols else None

        # Search input inside main page for single stock mode
        search_query = st.text_input(
            "🔎 Search company name or symbol", key="search_text_single")
        if search_query:
            matches = search_symbols(search_query)
            if matches:
                st.write("Matching companies and symbols:")
                for sym, desc in matches:
                    if st.button(f"{sym} — {desc}", key=f"btn_single_{sym}"):
                        _set_symbols_in_query([sym])
                        st.experimental_rerun()
            else:
                st.warning("No matches found.")

        if not symbol:
            st.info("Please search and select a company symbol above to proceed.")
            return

        render_single_stock(symbol)

    else:  # Compare Stocks mode
        search_query = st.text_input(
            "🔎 Search company names or symbols (comma separated)", key="search_text_compare")
        matched_symbols_set = set()
        if search_query:
            terms = [t.strip() for t in search_query.split(",") if t.strip()]
            for term in terms:
                matches = search_symbols(term)
                for sym, _ in matches:
                    matched_symbols_set.add(sym)

        matched_symbols = sorted(matched_symbols_set)

        selected_symbols = symbols if len(symbols) > 1 else matched_symbols[:2]

        if matched_symbols:
            selected_symbols = st.multiselect(
                "Select 2 to 10 stocks to compare from matched symbols",
                matched_symbols,
                default=selected_symbols,
                help="Select at least 2 and up to 10 stocks",
            )
            _set_symbols_in_query(selected_symbols)
        else:
            st.warning("No matching companies found.")

        if not selected_symbols or len(selected_symbols) < 2:
            st.info("Please select at least 2 company symbols above to compare.")
            return

        if len(selected_symbols) > 10:
            st.warning("Please select no more than 10 stocks.")
            selected_symbols = selected_symbols[:10]
            _set_symbols_in_query(selected_symbols)

        render_compare_stocks(selected_symbols)


if __name__ == "__main__":
    main()
