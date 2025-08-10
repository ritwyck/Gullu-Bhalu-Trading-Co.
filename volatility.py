import pandas as pd
import numpy as np


def realized_volatility(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.std()


def load_data(symbol):
    df = pd.read_csv(f"HistoricalData/{symbol}.csv")
    df["Close"] = df["Close"].replace(",", "", regex=True).astype(float)
    return df
