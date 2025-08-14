import pandas as pd
import numpy as np


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


def true_range(high, low, close):
    hl = high - low
    hc = (high - close.shift(1)).abs()
    lc = (low - close.shift(1)).abs()
    return pd.concat([hl, hc, lc], axis=1).max(axis=1)


def directional_movement(high, low):
    move_up = high.diff()
    move_down = low.shift(1) - low
    plus_dm = np.where((move_up > move_down) & (move_up > 0), move_up, 0.0)
    minus_dm = np.where((move_down > move_up) &
                        (move_down > 0), move_down, 0.0)
    return pd.Series(plus_dm, index=high.index), pd.Series(minus_dm, index=high.index)


def wilder_smoothing(series, period):
    smoothed = series.copy()
    smoothed.iloc[0:period] = np.nan
    first_val = series.iloc[0:period].sum()
    smoothed.iloc[period] = first_val
    for i in range(period+1, len(series)):
        smoothed.iloc[i] = smoothed.iloc[i-1] - \
            (smoothed.iloc[i-1] / period) + series.iloc[i]
    return smoothed


def calculate_di(plus_dm_smooth, minus_dm_smooth, atr):
    plus_di = (plus_dm_smooth / atr) * 100
    minus_di = (minus_dm_smooth / atr) * 100
    return plus_di, minus_di


def calculate_dx(plus_di, minus_di):
    return ((plus_di - minus_di).abs() / (plus_di + minus_di).abs()) * 100


def calculate_adx(dx, period):
    adx = dx.rolling(window=period, min_periods=period).mean()
    for i in range(period * 2, len(dx)):
        adx.iloc[i] = ((adx.iloc[i-1] * (period - 1)) + dx.iloc[i]) / period
    return adx

# ----------------- MAIN FUNCTION -----------------


def adx(high, low, close, period=14):
    tr = true_range(high, low, close)
    atr = wilder_smoothing(tr, period)
    plus_dm, minus_dm = directional_movement(high, low)
    plus_dm_smooth = wilder_smoothing(plus_dm, period)
    minus_dm_smooth = wilder_smoothing(minus_dm, period)
    plus_di, minus_di = calculate_di(plus_dm_smooth, minus_dm_smooth, atr)
    dx = calculate_dx(plus_di, minus_di)
    adx_values = calculate_adx(dx, period)
    return pd.DataFrame({
        "+DI": plus_di.round(1),
        "-DI": minus_di.round(1),
        "ADX": adx_values.round(1)
    })


# ----------------- TEST RUN -----------------
if __name__ == "__main__":
    df = pd.read_csv("Vault/Historical_Stock_Data/ADANIPORTS.csv")
    result = adx(df['High'], df['Low'], df['Close'], period=14)
    print(result.tail(10))
