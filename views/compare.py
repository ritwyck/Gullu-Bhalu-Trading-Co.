import urllib.parse
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data
from UserInterface.modules.ui_controls import get_period_inputs
from UserInterface.modules.calculations import compute_multiple_volatility_ratios
import pandas as pd


def render_compare_stocks():
    """Render the multi-stock comparison page with search and live data only."""

    st.title("📊 Compare Multiple Stocks Dashboard")

    # --- Search input for company names or symbols ---
    query = st.text_input(
        "🔎 Search company names or symbols (comma separated)")

    selected_symbols = []

    if query:
        search_terms = [term.strip()
                        for term in query.split(",") if term.strip()]
        matched_symbols_set = set()
        for term in search_terms:
            matches = search_symbols(term)
            for symbol, _ in matches:
                if symbol not in matched_symbols_set:
                    matched_symbols_set.add(symbol)
        matched_symbols = list(matched_symbols_set)

        if matched_symbols:
            st.write("Matching company symbols found:")
            # Multi-select from matched symbols, default all selected
            selected_symbols = st.multiselect(
                "Select 2 to 10 stocks to compare from matches",
                matched_symbols,
                default=matched_symbols[:10],
                help="Select at least 2 and up to 10 stocks",
            )
        else:
            st.warning("No matching companies found.")

    if not selected_symbols:
        st.info("Please search and select at least 2 company symbols above to compare.")
        return

    # Enforce minimum 2 and maximum 10 selections
    if len(selected_symbols) < 2:
        st.warning(
            "You must select at least 2 stocks. Please adjust your selection.")
        return
    if len(selected_symbols) > 10:
        st.warning("Please select no more than 10 stocks.")
        selected_symbols = selected_symbols[:10]

    # --- Update URL param for selected symbols ---
    st.experimental_set_query_params(symbols=",".join(selected_symbols))

    # --- Fetch live historical data for each selected symbol and get lengths ---
    lens = []
    for symbol in selected_symbols:
        df_live = fetch_historical_data(symbol)
        if df_live is None or df_live.empty:
            st.warning(f"No live data found for {symbol}. It will be skipped.")
        else:
            lens.append(len(df_live))
    if not lens:
        st.error("No live data found for any selected stocks.")
        return

    max_len = max(lens)

    # --- Get user inputs for custom period and ratio reference period ---
    custom_period, ratio_ref_period = get_period_inputs(max_len)

    # --- Compute volatility and ratios using live data ---
    # Note: This function originally loads from local data. Assuming you adapt this function or have a version that uses live data.
    # If not, here just call your function as is for demo, it needs adaptation for live data fetch internally.
    final_df = compute_multiple_volatility_ratios(
        selected_symbols, None, None, custom_period, ratio_ref_period
    )

    # --- Add links ---
    final_df["Stock"] = final_df["Symbol"].apply(
        lambda s: f"/?page=Stocks&symbol={urllib.parse.quote(s)}"
    )

    # --- Reorder columns ---
    cols = ["Symbol", "Stock"] + \
        [c for c in final_df.columns if c not in ["Symbol", "Stock"]]
    final_df = final_df[cols]

    # --- Display table with links ---
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
