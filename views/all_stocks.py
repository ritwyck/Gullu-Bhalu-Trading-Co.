import os
import urllib.parse
import pandas as pd
import streamlit as st
from Backend.Strategy.volatility import load_data, historical_volatility


def render_all_stocks(data_folder="Vault/Historical_Stock_Data"):
    """Render the all-stocks volatility & ratio page."""
    # --- Load files & symbols ---
    files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    symbols = [os.path.splitext(f)[0] for f in files]

    # --- User inputs ---
    custom_period = st.number_input("Volatility period (days)", 2, 365, 10)
    ratio_ref_period = st.number_input(
        "Reference period for ratios (days)", 2, 365, 5
    )

    rows = []
    for sym in symbols:
        df = load_data(os.path.join(data_folder, f"{sym}.csv"))

        # reference volatility
        ref_vol = None
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"]
            )

        # compute vols
        periods = sorted({5, 10, 30, 100, custom_period})
        row_fields = {
            f"Vol_{p}d": round(historical_volatility(df.tail(p)["Close"])[1], 3)
            for p in periods
            if p <= len(df)
        }

        # compute ratios
        row_fields.update(
            {
                f"Ratio_{p}d": round(row_fields[f"Vol_{p}d"] / ref_vol, 3)
                if ref_vol and f"Vol_{p}d" in row_fields
                else pd.NA
                for p in periods
            }
        )

        # add row
        rows.append(
            {
                "Symbol": sym,
                "Stock": f"/?page=Stocks&symbol={urllib.parse.quote(sym)}",
                **row_fields,
            }
        )

    # --- Build dataframe ---
    df = pd.DataFrame(rows)
    df["Compare"] = False

    st.subheader("Volatility & Ratios Table")
    edited = st.data_editor(
        df,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
            "Stock": st.column_config.LinkColumn("Stock", display_text="View"),
            "Compare": st.column_config.CheckboxColumn("Compare"),
        },
        hide_index=True,
        key="stock_compare_editor",
    )

    selected = edited.loc[edited["Compare"], "Symbol"].tolist()
    if selected:
        # Step 1: join selected symbols with comma
        joined = ",".join(selected)
    # Step 2: URL-encode the string
        encoded = urllib.parse.quote(joined)
    # Step 3: build compare URL using %2C (standard URL-encoded comma)
        compare_url = f"/?page=Compare-Stocks&symbols={encoded}"

        st.markdown(
            f"""
        <a href="{compare_url}">
            <button style="
                background-color:#4CAF50;
                border:none;
                color:white;
                padding:10px 20px;
                text-align:center;
                text-decoration:none;
                display:inline-block;
                font-size:16px;
                border-radius:8px;
                cursor:pointer;
            ">
            🔗 Compare Selected Stocks
            </button>
        </a>
        """,
            unsafe_allow_html=True,
        )
