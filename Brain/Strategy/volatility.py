import pandas as pd
import numpy as np


def realized_volatility(prices):
    """
    Calculate realized volatility from a price series.
    Returns value rounded to 3 decimal places.
    """
    returns = np.log(prices / prices.shift(1)).dropna()
    return round(returns.std(), 3)


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    # Only clean Close if it's string/object type
    if df["Close"].dtype == object:
        df["Close"] = df["Close"].str.replace(",", "").astype(float)
    return df


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """Step 1: Calculate log returns from price series."""
    return np.log(prices / prices.shift(1)).dropna()


def calculate_mean_return(log_returns: pd.Series) -> float:
    """Step 2: Calculate mean of log returns."""
    return log_returns.mean()


def calculate_squared_diffs(log_returns: pd.Series, mean_return: float) -> pd.Series:
    """Step 3: Calculate squared differences from the mean return."""
    return (log_returns - mean_return) ** 2


def calculate_variance(squared_diffs: pd.Series) -> float:
    """Step 4: Calculate sample variance from squared differences."""
    return squared_diffs.sum() / (len(squared_diffs) - 1)


def calculate_volatility(variance: float) -> float:
    """Step 5: Calculate volatility as standard deviation."""
    return np.sqrt(variance)


# def annualize_volatility(volatility: float, periods_per_year: int = 252) -> float:
 #   """Step 6: Convert volatility to annualized volatility."""
  #  return volatility * np.sqrt(periods_per_year)


def historical_volatility(prices: pd.Series, periods_per_year: int = 252):
    """Main function to compute raw and annualized historical volatility."""
    log_returns = calculate_log_returns(prices)
    mean_return = calculate_mean_return(log_returns)
    squared_diffs = calculate_squared_diffs(log_returns, mean_return)
    variance = calculate_variance(squared_diffs)
    volatility = calculate_volatility(variance)
   # annualized_vol = annualize_volatility(volatility, periods_per_year)
    return round(volatility)


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
    return f"{(vol1 / vol2) * 100:.3f}"
