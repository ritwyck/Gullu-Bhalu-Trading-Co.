import pandas as pd
import numpy as np


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Calculate the True Range (TR) for each period."""
    high_low = high - low
    high_close = (high - close.shift(1)).abs()
    low_close = (low - close.shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr


def directional_movement(high: pd.Series, low: pd.Series):
    """
    Calculate the Plus Directional Movement (+DM) and Minus Directional Movement (-DM)
    with Wilder's mutual exclusion logic.
    """
    move_up = high.diff()
    move_down = low.shift(1) - low

    plus_dm = np.where((move_up > move_down) & (move_up > 0), move_up, 0.0)
    minus_dm = np.where((move_down > move_up) &
                        (move_down > 0), move_down, 0.0)

    return pd.Series(plus_dm, index=high.index), pd.Series(minus_dm, index=high.index)


def wilder_smoothing(series: pd.Series, period: int) -> pd.Series:
    """
    Wilder's smoothing (Recursive).
    The first value is the sum of the first 'period' values.
    Subsequent values use: prev_smoothed - (prev_smoothed / period) + current_value
    """
    smoothed = series.copy()
    smoothed.iloc[0:period] = np.nan  # no smoothing until enough data
    first_val = series.iloc[0:period].sum()
    smoothed.iloc[period] = first_val
    for i in range(period + 1, len(series)):
        smoothed.iloc[i] = smoothed.iloc[i - 1] - \
            (smoothed.iloc[i - 1] / period) + series.iloc[i]
    return smoothed


def calculate_di(plus_dm_smoothed: pd.Series, minus_dm_smoothed: pd.Series, atr: pd.Series):
    """Calculate Plus DI and Minus DI."""
    plus_di = (plus_dm_smoothed / atr) * 100
    minus_di = (minus_dm_smoothed / atr) * 100
    return plus_di, minus_di


def calculate_dx(plus_di: pd.Series, minus_di: pd.Series) -> pd.Series:
    """Calculate the Directional Movement Index (DX)."""
    return ((plus_di - minus_di).abs() / (plus_di + minus_di).abs()) * 100


def calculate_adx(dx: pd.Series, period: int) -> pd.Series:
    """Smooth the DX values to get the ADX."""
    adx = dx.rolling(window=period, min_periods=period).mean(
    )  # Seed with SMA of first period
    for i in range(period * 2, len(dx)):
        adx.iloc[i] = ((adx.iloc[i - 1] * (period - 1)) +
                       dx.iloc[i]) / period  # Wilder's smoothing
    return adx


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    """
    Calculate ADX, +DI, and -DI using Welles Wilder's method.
    Returns DataFrame with columns: +DI, -DI, ADX
    """
    # Step 1: True Range & ATR
    tr = true_range(high, low, close)
    atr = wilder_smoothing(tr, period)

    # Step 2 & 3: Directional Movements
    plus_dm, minus_dm = directional_movement(high, low)

    # Step 4 & 5: Smooth +DM and -DM
    plus_dm_smoothed = wilder_smoothing(plus_dm, period)
    minus_dm_smoothed = wilder_smoothing(minus_dm, period)

    # Step 6: DIs
    plus_di, minus_di = calculate_di(plus_dm_smoothed, minus_dm_smoothed, atr)

    # Step 7: DX
    dx = calculate_dx(plus_di, minus_di)

    # Step 8: ADX
    adx_values = calculate_adx(dx, period)

    return pd.DataFrame({
        '+DI': plus_di,
        '-DI': minus_di,
        'ADX': adx_values
    })
