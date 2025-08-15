import numpy as np
import pandas as pd


def wilder_smooth(values, period):
    """Matches TradingView more closely: first smoothed value = mean of first period."""
    values = np.array(values, dtype=float)
    smoothed = np.full_like(values, np.nan)
    smoothed[period-1] = np.nanmean(values[:period])  # mean, not sum
    for i in range(period, len(values)):
        smoothed[i] = smoothed[i-1] - (smoothed[i-1] / period) + values[i]
    return smoothed


def calculate_adx(highs, lows, closes, period=14):
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)

    # 1️⃣ True Range (TR)
    prev_close = np.roll(closes, 1)
    prev_close[0] = np.nan
    tr = np.maximum.reduce([
        highs - lows,
        np.abs(highs - prev_close),
        np.abs(lows - prev_close)
    ])

    # 2️⃣ Directional Movement
    up_move = highs[1:] - highs[:-1]
    down_move = lows[:-1] - lows[1:]

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) &
                        (down_move > 0), down_move, 0.0)
    plus_dm = np.insert(plus_dm, 0, np.nan)
    minus_dm = np.insert(minus_dm, 0, np.nan)

    # 3️⃣ Wilder smoothing (first smoothed = mean of first period)
    def wilder_smooth_tv(values):
        values = np.array(values, dtype=float)
        smoothed = np.full_like(values, np.nan)
        smoothed[period-1] = np.nanmean(values[:period])
        for i in range(period, len(values)):
            smoothed[i] = smoothed[i-1] - (smoothed[i-1] / period) + values[i]
        return smoothed

    sm_tr = wilder_smooth_tv(tr)
    sm_plus_dm = wilder_smooth_tv(plus_dm)
    sm_minus_dm = wilder_smooth_tv(minus_dm)

    # 4️⃣ DI calculation
    plus_di = 100 * (sm_plus_dm / sm_tr)
    minus_di = 100 * (sm_minus_dm / sm_tr)

    # 5️⃣ DX and ADX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = wilder_smooth_tv(dx)

    return pd.DataFrame({
        '+DI': plus_di,
        '-DI': minus_di,
        'ADX': adx
    })
