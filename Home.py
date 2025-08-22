import pandas as pd
import streamlit as st
from UserInterface.modules.symbol_search import get_symbols as search_symbols
from UserInterface.modules.data_acquisition import fetch_historical_data, _get_live, _get_symbols_from_query, _set_symbols_in_query
from UserInterface.modules.ui_controls import get_metric_and_window, get_period_inputs
from UserInterface.modules.plot import plot_stock_metric
from UserInterface.modules.calculations import compute_volatility_and_ratios, compute_adx_table
from Page.singleStock import render_single_stock
from Page.multipleStock import render_multi_stocks
import plotly.graph_objects as go


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

            render_multi_stocks(selected_symbols)


if __name__ == "__main__":
    main()
