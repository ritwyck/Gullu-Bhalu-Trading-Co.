import pandas_ta as ta
import yfinance as yf
import pandas as pd
import numpy as np
import talib
from ta.trend import ADXIndicator
import pandas_ta as pta

# --- TA-Lib based function ---


def get_adx_talib(high, low, close, period=14):
    return talib.ADX(high, low, close, timeperiod=period)

# --- Custom TradingView-style ADX ---


def calculate_adx_tradingview(high, low, close, period=14):
    high = np.array(high, dtype=float)
    low = np.array(low, dtype=float)
    close = np.array(close, dtype=float)

    up_move = high[1:] - high[:-1]
    down_move = low[:-1] - low[1:]

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    true_range = np.maximum.reduce([tr1, tr2, tr3])

    def wilder_smooth(data, period):
        smoothed = np.zeros(len(data) - period + 1)
        smoothed[0] = np.sum(data[:period])
        for i in range(period, len(data)):
            smoothed[i - period + 1] = smoothed[i - period] - \
                (smoothed[i - period] / period) + data[i]
        return smoothed

    tr_smooth = wilder_smooth(true_range, period)
    plus_dm_smooth = wilder_smooth(plus_dm, period)
    minus_dm_smooth = wilder_smooth(minus_dm, period)

    plus_di = 100 * plus_dm_smooth / tr_smooth
    minus_di = 100 * minus_dm_smooth / tr_smooth

    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)

    adx = np.zeros(len(dx) - period + 1)
    adx[0] = np.mean(dx[:period])
    for i in range(1, len(adx)):
        adx[i] = ((adx[i - 1] * (period - 1)) + dx[i + period - 1]) / period

    return adx


# --- MAIN COMPARISON ---
file_path = "Vault/Historical_Stock_Data/RELIANCE.csv"  # your 6-month CSV
data = pd.read_csv(file_path)

# Ensure data is sorted
if 'Date' in data.columns:
    data = data.sort_values('Date')

# Input arrays
high = data['High'].values
low = data['Low'].values
close = data['Close'].values

# TA-Lib ADX
adx_talib = get_adx_talib(high, low, close, period=14)

# Custom ADX
adx_tv = calculate_adx_tradingview(high, low, close, period=14)

# Because the custom function shortens output, align lengths
# We'll pad with NaNs to match TA-Lib's output indexing
adx_tv_aligned = np.concatenate(
    [np.full(len(adx_talib) - len(adx_tv), np.nan), adx_tv])

# Combine into DataFrame for easy comparison
compare_df = pd.DataFrame({
    'Date': data['Date'],
    'ADX_TA_Lib': adx_talib,
    'ADX_TradingViewStyle': adx_tv_aligned
})

# Show last few rows
print(compare_df.tail(10))

# Last values
print("\nLast ADX (TA-Lib):", round(adx_talib[-1], 4))
print("Last ADX (TradingView-style):", round(adx_tv[-1], 4))
print("Difference:", round(adx_talib[-1] - adx_tv[-1], 4))

symbol = "RELIANCE.NS"  # Example symbol, change as needed
df = yf.download(symbol, period="6mo", interval="1d")

# Flatten MultiIndex columns
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Check columns
print(df.columns)

# Compute ADX
adx = ta.adx(high=df['High'], low=df['Low'], close=df['Close'], length=14)

if adx is not None:
    df['ADX'] = adx.iloc[:, 0]
    print(df[['High', 'Low', 'Close', 'ADX']].tail())
else:
    print("ADX computation failed. Check your data and column names.")
