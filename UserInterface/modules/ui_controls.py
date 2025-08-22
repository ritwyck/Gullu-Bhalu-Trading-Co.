import streamlit as st


def select_symbol(symbols):
    params = st.query_params
    default_symbol = params.get(
        "symbol", [None]) if "symbol" in params else None
    default_index = symbols.index(
        default_symbol) if default_symbol in symbols else 0
    return st.selectbox("Select stock symbol", symbols, index=default_index)


def select_symbols(symbols):
    params = st.query_params
    selected_symbols = None
    if "symbols" in params:
        selected_symbols = params["symbols"].split(",")
    # fallback to session state etc.
    if selected_symbols is None and "selected_symbols" in st.session_state:
        if st.session_state.selected_symbols:
            selected_symbols = list(st.session_state.selected_symbols)
    if not selected_symbols:
        selected_symbols = st.multiselect(
            "Select 2 to 10 stocks to compare",
            symbols,
            default=symbols[:2]
        )
    return selected_symbols


def get_metric_and_window(metric_options, key):
    metric = st.radio(
        "Select metric to plot", metric_options, key=key
    )
    window = 10
    if metric == "Volatility":
        window = st.number_input(
            "Volatility rolling window", min_value=2, max_value=100, value=10, key=f"{key}_window"
        )
    return metric, window


def get_period_inputs(df_len, key_prefix=""):
    fixed_periods = [5, 10, 15, 30, 60, 100]

    custom_period = st.number_input(
        "Select Volatility period in days",
        min_value=2, max_value=df_len,
        value=min(10, df_len),  # make sure default <= df_len
        key=f"{key_prefix}_custom_vol_period"
    )

    if custom_period not in fixed_periods:
        fixed_periods.append(custom_period)
    fixed_periods = sorted(fixed_periods)

    ratio_ref_period = st.number_input(
        "Select Ratio period in days",
        min_value=2, max_value=df_len,
        value=min(5, df_len),  # clamp again
        step=1, key=f"{key_prefix}_ratio_ref_period"
    )

    return fixed_periods, ratio_ref_period
