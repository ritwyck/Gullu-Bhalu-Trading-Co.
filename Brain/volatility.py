import pandas as pd
import numpy as np


def realized_volatility(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.std()


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    # Only clean Close if it's string/object type
    if df["Close"].dtype == object:
        df["Close"] = df["Close"].str.replace(",", "").astype(float)
    return df


#! must be worked on
def historical_volatility(prices, periods_per_year=252):
    # Step 1: Calculate log returns
    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Step 2: Mean of log returns
    mean_return = log_returns.mean()

    # Step 3: Squared differences from mean
    squared_diffs = (log_returns - mean_return) ** 2

    # Step 4: Variance (sample)
    variance = squared_diffs.sum() / (len(log_returns) - 1)

    # Step 5: Standard deviation
    volatility = np.sqrt(variance)

    # Annualize
    annualized_vol = volatility * np.sqrt(periods_per_year)

    return volatility, annualized_vol


def volatility_ratio(vol1, vol2=100.0):
    """
    Calculate the volatility ratio between two volatility values.

    Parameters:
    - vol1: float or int, first volatility value
    - vol2: float or int, second volatility value (default = 100.0)

    Returns:
    - ratio: float, ratio as (vol1 / vol2) * 100
    """
    if vol2 == 0:
        return float('nan')
    return (vol1 / vol2) * 100
