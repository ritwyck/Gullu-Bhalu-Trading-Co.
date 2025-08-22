import pandas as pd
import streamlit as st
from datetime import timedelta
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table


@st.cache_data(show_spinner=False)
def _get_live(symbol: str) -> pd.DataFrame | None:
    try:
        df = fetch_historical_data(symbol)
        if df is None or df.empty:
            return None
        # Ensure DatetimeIndex, drop tz for safe comparisons
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].copy()
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert(None)
        return df.sort_index()
    except Exception:
        return None


def _get_symbol_from_query() -> str | None:
    qp = st.query_params
    return qp.get("symbol") if isinstance(qp.get("symbol"), str) else None


def _set_symbol_in_query(symbol: str) -> None:
    st.query_params["symbol"] = symbol


def render_single_stock():
    """Render the single stock analysis page with search and live data only."""
    st.title("📈 Trade Jockey Dashboard")

    # --- Read symbol from URL if present ---
    selected_symbol = _get_symbol_from_query()

    # --- Search input for company name or symbol ---
    query = st.text_input("🔎 Search company name or symbol", value="")

    if query:
        matches = search_symbols(query)  # List[Tuple[symbol, description]]
        if matches:
            st.write("Matching companies and symbols:")
            for symbol, description in matches:
                if st.button(f"{symbol} — {description}", key=f"symbtn_{symbol}"):
                    selected_symbol = symbol
                    _set_symbol_in_query(symbol)
                    st.rerun()
        else:
            st.warning("No matches found.")

    # --- Require symbol selection ---
    if not selected_symbol:
        st.info("Please search and select a company symbol above to proceed.")
        return

    # --- Fetch live historical data for selected symbol ---
    df_live = _get_live(selected_symbol)
    if df_live is None or df_live.empty:
        st.error(f"No live historical data found for '{selected_symbol}'.")
        return

    # --- Last week OHLC table (no plot here) ---
    start_ts = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=7)
    last_week_df = df_live.loc[df_live.index >= start_ts]

    ohlc_cols = [c for c in ["Open", "High",
                             "Low", "Close"] if c in df_live.columns]

    if not last_week_df.empty and ohlc_cols:
        st.subheader(f"{selected_symbol} — Last Week OHLC Data")
        st.dataframe(last_week_df.loc[:, ohlc_cols])
    else:
        st.info("No recent last-week OHLC data available.")

    # --- Metric controls & plotting (single chart only) ---
    metric, window = get_metric_and_window(
        ["Open", "High", "Low", "Close", "Volatility"], "single_metric"
    )
    df_for_plot = df_live.reset_index().rename(columns={"index": "Date"})
    plot_stock_metric(df_for_plot, metric, window if metric ==
                      "Volatility" else None)

    # --- Compute volatility, ratios, and ADX ---
    fixed_periods, ratio_ref_period = get_period_inputs(len(df_live))
    vol_rows = compute_volatility_and_ratios(
        df_live, fixed_periods, ratio_ref_period)
    adx_rows = compute_adx_table(df_live, fixed_periods)

    # --- Display tables ---
    st.subheader(f"{selected_symbol} — Volatility & Ratio Table")
    st.dataframe(pd.DataFrame(vol_rows))

    st.subheader(f"{selected_symbol} — ADX Table")
    st.dataframe(pd.DataFrame(adx_rows))


if __name__ == "__main__":
    render_single_stock()
