import numpy as np
import pandas as pd
from Logic.Strategy.volatility import historical_volatility
from Logic.Strategy.adx import calculate_adx
from UserInterface.modules.data_loading import load_symbol_data


def compute_multiple_volatility_ratios(
    selected_symbols, files, data_folder, custom_period, ratio_ref_period
):
    """
    Compute volatility and ratios for multiple symbols.

    - Volatility is calculated using historical_volatility (annualized).
    - Vol_{p}d columns contain the volatilities for each period p.
    - Ratio_{p}d columns contain the ratio relative to ratio_ref_period.

    Parameters
    ----------
    selected_symbols : list[str]
        List of symbol tickers to process.
    files : dict or list
        Reference to available data files (passed to load_symbol_data).
    data_folder : str or pathlib.Path
        Base folder where input data is stored.
    custom_period : int | list[int]
        Custom lookback period (days). If list, first element is used.
    ratio_ref_period : int | list[int]
        Reference period for ratio calculations. If list, first element is used.

    Returns
    -------
    pd.DataFrame
        Table of volatilities and ratios by symbol.
    """

    # Defensive conversion for cases where query params pass lists
    if isinstance(custom_period, list):
        custom_period = int(custom_period[0])
    if isinstance(ratio_ref_period, list):
        ratio_ref_period = int(ratio_ref_period)

    fixed_periods = [5, 10, 30, 100]
    all_rows = []

    for sym in selected_symbols:
        df = load_symbol_data(data_folder, sym, files)
        if df is None or "Close" not in df.columns:
            continue

        # combine fixed + custom periods
        periods = fixed_periods.copy()
        if custom_period not in periods:
            periods.append(custom_period)
        periods = sorted(periods)

        row = {"Symbol": sym}

        # reference vol only if we have enough data
        if ratio_ref_period <= len(df):
            _, ref_vol = historical_volatility(
                df.tail(ratio_ref_period)["Close"])
        else:
            ref_vol = None

        # Compute volatility for each period
        for p in periods:
            if p <= len(df):
                _, vol = historical_volatility(df.tail(p)["Close"])
                row[f"Vol_{p}d"] = round(vol, 3) if vol is not None else pd.NA
            else:
                row[f"Vol_{p}d"] = pd.NA

        # Compute ratio vs reference
        for p in periods:
            if p <= len(df):
                _, vol = historical_volatility(df.tail(p)["Close"])
                if ref_vol and ref_vol != 0:
                    ratio_val = vol / ref_vol
                else:
                    ratio_val = None
                row[f"Ratio_{p}d"] = round(
                    ratio_val, 3) if ratio_val else pd.NA
            else:
                row[f"Ratio_{p}d"] = pd.NA

        all_rows.append(row)

    return pd.DataFrame(all_rows).round(3)


def _last_valid(s: pd.Series) -> float | None:
    if s is None:
        return None
    s = s.dropna()
    return float(s.iloc[-1]) if len(s) else None


def _r(x, n):
    return round(float(x), n) if x is not None and np.isfinite(x) else None


def _wilder_rma(s: pd.Series, period: int) -> pd.Series:
    # Wilder's smoothing = EMA with alpha = 1/period, adjust=False
    return s.ewm(alpha=1/period, adjust=False, min_periods=period).mean()


def compute_volatility_and_ratios(df: pd.DataFrame, periods: list[int], ratio_ref_period: int):
    """
    Volatility: rolling std of log returns (annualized).
    Ratio: vol(period) / vol(ratio_ref_period).
    """
    rows: list[dict] = []
    if "Close" not in df.columns or len(df) < 3:
        return rows

    close = df["Close"].astype(float)
    logret = np.log(close).diff()

    # reference volatility
    ref_series = logret.rolling(
        ratio_ref_period, min_periods=ratio_ref_period).std(ddof=0) * np.sqrt(252)
    ref_vol = _last_valid(ref_series)

    for p in sorted(set(periods)):
        if len(df) < p + 2:
            rows.append({"Period (days)": p, "Volatility": None,
                        f"Ratio vs {ratio_ref_period}d": None})
            continue

        vol_series = logret.rolling(
            p, min_periods=p).std(ddof=0) * np.sqrt(252)
        vol = _last_valid(vol_series)

        ratio = (
            vol / ref_vol) if (vol is not None and ref_vol and ref_vol > 0) else None

        rows.append({
            "Period (days)": p,
            "Volatility": _r(vol, 4),
            f"Ratio vs {ratio_ref_period}d": _r(ratio, 3),
        })
    return rows


def compute_adx_table(df: pd.DataFrame, periods: list[int]):
    """
    ADX using Wilder’s method. Also returns latest +DI and -DI.
    """
    if not {"High", "Low", "Close"}.issubset(df.columns):
        return []

    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)

    # True Range
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    # Directional Movement (raw)
    up_move = high.diff()
    down_move = low.shift(1) - low  # yesterday low - today low
    plus_dm_raw = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm_raw = np.where((down_move > up_move) &
                            (down_move > 0), down_move, 0.0)

    plus_dm = pd.Series(plus_dm_raw, index=high.index)
    minus_dm = pd.Series(minus_dm_raw, index=high.index)

    rows: list[dict] = []
    for p in sorted(set(periods)):
        if len(df) < p + 2:
            rows.append({"Period (days)": p, "+DI": None,
                        "-DI": None, "ADX": None})
            continue

        tr_rma = _wilder_rma(tr, p)
        plus_rma = _wilder_rma(plus_dm, p)
        minus_rma = _wilder_rma(minus_dm, p)

        plus_di = 100 * (plus_rma / tr_rma.replace(0, np.nan))
        minus_di = 100 * (minus_rma / tr_rma.replace(0, np.nan))

        sum_di = (plus_di + minus_di).replace(0, np.nan)
        dx = ((plus_di - minus_di).abs() / sum_di) * 100
        adx = _wilder_rma(dx, p)

        rows.append({
            "Period (days)": p,
            "+DI": _r(_last_valid(plus_di), 2),
            "-DI": _r(_last_valid(minus_di), 2),
            "ADX": _r(_last_valid(adx), 2),
        })
    return rows
