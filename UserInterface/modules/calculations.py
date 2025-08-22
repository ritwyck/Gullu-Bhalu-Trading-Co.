import numpy as np
import pandas as pd
from Logic.Strategy.volatility import historical_volatility
from Logic.Strategy.adx import calculate_adx
from UserInterface.modules.data_loading import load_symbol_data


def compute_volatility_and_ratios(df: pd.DataFrame, periods: list[int], ratio_ref_period: int):
    """
    Compute rolling volatility (std of log returns) and price ratios.
    Returns a list of dict rows for display.
    """
    rows = []

    # Daily log returns
    if "Close" not in df.columns:
        return rows
    df = df.copy()
    df["LogReturn"] = np.log(df["Close"] / df["Close"].shift(1))

    for p in periods:
        vol = df["LogReturn"].rolling(
            p).std().iloc[-1] * np.sqrt(252)  # annualized
        ratio = None
        if ratio_ref_period in df.index[-p:].shape:
            # fallback if ref period too large
            ratio = df["Close"].iloc[-1] / \
                df["Close"].iloc[-ratio_ref_period] - 1
        else:
            if len(df) > ratio_ref_period:
                ratio = df["Close"].iloc[-1] / \
                    df["Close"].iloc[-ratio_ref_period] - 1

        rows.append({
            "Period (days)": p,
            "Volatility": round(vol, 4) if pd.notna(vol) else None,
            f"Return vs {ratio_ref_period}d": round(ratio, 4) if ratio is not None else None
        })
    return rows


def compute_multiple_volatility_ratios(selected_symbols, files, data_folder, custom_period, ratio_ref_period):
    # Defensive conversion for inputs that might be lists from query params
    if isinstance(custom_period, list):
        custom_period = int(custom_period[0])
    if isinstance(ratio_ref_period, list):
        ratio_ref_period = int(ratio_ref_period[0])

    fixed_periods = [5, 10, 30, 100]
    all_rows = []
    for sym in selected_symbols:
        df = load_symbol_data(data_folder, sym, files)
        if df is None:
            continue
        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)
        row_data = {"Symbol": sym}
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                row_data[f"Vol_{p}d"] = round(annual_vol, 3)
        for p in periods:
            if p <= len(df):
                _, annual_vol = historical_volatility(df.tail(p)["Close"])
                ratio_val = (
                    annual_vol / ref_vol) if (ref_vol and ref_vol != 0) else pd.NA
                row_data[f"Ratio_{p}d"] = round(
                    ratio_val, 3) if ratio_val is not pd.NA else pd.NA
        all_rows.append(row_data)
    final_df = pd.DataFrame(all_rows).round(3)
    return final_df


def compute_adx_table(df: pd.DataFrame, periods: list[int]):
    """
    Compute ADX (trend strength) for given periods.
    Returns a list of dict rows for display.
    """
    if not {"High", "Low", "Close"}.issubset(df.columns):
        return []

    rows = []

    high, low, close = df["High"], df["Low"], df["Close"]

    def compute_adx(period: int):
        # True Range
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(period).mean()

        # Directional Movement
        plus_dm = high.diff()
        minus_dm = low.diff().abs()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(period).mean()

        return adx.iloc[-1]

    for p in periods:
        adx_val = compute_adx(p)
        rows.append({
            "Period (days)": p,
            "ADX": round(adx_val, 2) if pd.notna(adx_val) else None
        })

    return rows
