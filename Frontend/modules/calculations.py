import numpy as np
import pandas as pd
from Backend.Strategy.volatility import historical_volatility
from Backend.Strategy.adx import calculate_adx
from Frontend.modules.data_loading import load_symbol_data


def compute_volatility_and_ratios(df, fixed_periods, ratio_ref_period):
    # Defensive conversion if ratio_ref_period is list
    if isinstance(ratio_ref_period, list):
        ratio_ref_period = int(ratio_ref_period[0])

    _, ref_vol = historical_volatility(df["Close"].tail(ratio_ref_period))
    vol_rows = []
    for p in fixed_periods:
        # Defensive conversion if p is list
        if isinstance(p, list):
            p = int(p[0])

        annual_vol = ratio_val = None
        if p <= len(df):
            _, annual_vol = historical_volatility(df["Close"].tail(p))
            if ref_vol and ref_vol != 0:
                ratio_val = annual_vol / ref_vol
        vol_rows.append({
            "Volatility Period": p,
            "Historical Volatility": round(annual_vol, 3) if annual_vol is not None else None,
            f"Ratio vs {ratio_ref_period}d": round(ratio_val, 3) if ratio_val is not None else None
        })
    return vol_rows


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


def compute_adx_table(df, fixed_periods, adx_period=14):
    adx_rows = []
    for p in fixed_periods:
        # Defensive conversion if necessary
        if isinstance(p, list):
            p = int(p[0])

        plus_di_val = minus_di_val = adx_val = None
        if p >= adx_period and p <= len(df):
            df_slice = df.tail(p)
            adx_df = calculate_adx(
                df_slice["High"].values,
                df_slice["Low"].values,
                df_slice["Close"].values,
                period=adx_period
            )
            plus_di_val = round(
                adx_df["+DI"].iloc[-1], 1) if not np.isnan(adx_df["+DI"].iloc[-1]) else None
            minus_di_val = round(
                adx_df["-DI"].iloc[-1], 1) if not np.isnan(adx_df["-DI"].iloc[-1]) else None
            adx_val = round(
                adx_df["ADX"].iloc[-1], 1) if not np.isnan(adx_df["ADX"].iloc[-1]) else None
        adx_rows.append({
            "Period": p,
            "+DI": plus_di_val,
            "-DI": minus_di_val,
            "ADX": adx_val
        })
    return adx_rows
