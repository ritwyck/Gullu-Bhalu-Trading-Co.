import urllib.parse
import streamlit as st
import pandas as pd
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_period_inputs
from UserInterface.modules.calculations import compute_multiple_volatility_ratios


# Cache only during session; data is discarded when the session ends
@st.cache_data(show_spinner=False)
def _get_live(symbol: str) -> pd.DataFrame | None:
    """Safe wrapper around fetch_historical_data with normalized DatetimeIndex."""
    try:
        df = fetch_historical_data(symbol)
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
    if isinstance(val, list):
        return val
    return []


def _set_symbols_in_query(symbols: list[str]) -> None:
    st.query_params["symbol"] = symbols


def render_compare_stocks():
    """Render the multi-stock comparison page with search and live data only."""

    st.title("📊 Compare Multiple Stocks Dashboard")

    # --- Prepopulate from URL params if present ---
    selected_symbols = _get_symbols_from_query()

    # --- Search input for company names or symbols ---
    query = st.text_input(
        "🔎 Search company names or symbols (comma separated)", value=""
    )

    if query:
        search_terms = [term.strip()
                        for term in query.split(",") if term.strip()]
        matched_symbols_set = set()
        for term in search_terms:
            matches = search_symbols(term)
            for symbol, _ in matches:
                matched_symbols_set.add(symbol)

        matched_symbols = sorted(matched_symbols_set)

        if matched_symbols:
            st.write("Matching company symbols found:")
            selected_symbols = st.multiselect(
                "Select 2 to 10 stocks to compare from matches",
                matched_symbols,
                default=selected_symbols if selected_symbols else matched_symbols[:2],
                help="Select at least 2 and up to 10 stocks",
            )
            _set_symbols_in_query(selected_symbols)
        else:
            st.warning("No matching companies found.")

    if not selected_symbols:
        st.info("Please search and select at least 2 company symbols above to compare.")
        return

    # --- Enforce bounds ---
    if len(selected_symbols) < 2:
        st.warning("You must select at least 2 stocks.")
        return
    if len(selected_symbols) > 10:
        st.warning("Please select no more than 10 stocks.")
        selected_symbols = selected_symbols[:10]
        _set_symbols_in_query(selected_symbols)

    # --- Fetch live data ---
    lens = {}
    for sym in selected_symbols:
        df_live = _get_live(sym)
        if df_live is None or df_live.empty:
            st.warning(f"No live data found for {sym}. It will be skipped.")
        else:
            lens[sym] = len(df_live)

    if not lens:
        st.error("No live data found for any selected stocks.")
        return

    max_len = max(lens.values())

    # --- Get user inputs for period and ratio reference ---
    custom_period, ratio_ref_period = get_period_inputs(max_len)

    # --- Compute volatility & ratios ---
    final_df = compute_multiple_volatility_ratios(
        selected_symbols, None, None, custom_period, ratio_ref_period
    )

    if final_df is None or final_df.empty:
        st.error("Could not compute volatility/ratios for the selected stocks.")
        return

    # --- Add clickable links ---
    if "Symbol" in final_df.columns:
        final_df["Stock"] = final_df["Symbol"].apply(
            lambda s: f"/?page=Stocks&symbol={urllib.parse.quote(s)}"
        )

        # --- Reorder columns ---
        cols = ["Symbol", "Stock"] + [
            c for c in final_df.columns if c not in ["Symbol", "Stock"]
        ]
        final_df = final_df[cols]

    # --- Display interactive table ---
    st.subheader("Volatility & Ratios Table")
    st.data_editor(
        final_df,
        column_config={
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
        },
        hide_index=True,
        key="compare_stocks_editor",
    )


if __name__ == "__main__":
    render_compare_stocks()
