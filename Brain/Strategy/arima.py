# arima.py

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
import matplotlib.pyplot as plt


class ARIMAModel:
    def __init__(self, p=1, d=0, q=1):
        """
        Initialize the ARIMA model with parameters (p,d,q).
        p: number of autoregressive terms
        d: degree of differencing to achieve stationarity
        q: number of moving average terms
        """
        self.p = p
        self.d = d
        self.q = q
        self.model_fit = None
        self.fitted_values = None
        self.residuals = None

    def difference(self, series):
        """
        Difference the series d times to achieve stationarity.
        """
        differenced = series.copy()
        for _ in range(self.d):
            differenced = differenced.diff().dropna()
        return differenced

    def check_stationarity(self, series, significance=0.05):
        """
        Perform Augmented Dickey-Fuller test to check stationarity.
        Returns True if series is stationary, False otherwise.
        """
        result = adfuller(series.dropna())
        pvalue = result[1]
        print(f"ADF Test p-value: {pvalue}")
        return pvalue < significance

    def fit(self, series):
        """
        Fit the ARIMA model on the given time series data (pandas Series).
        """
        # Differencing if needed
        if self.d > 0:
            series_to_fit = self.difference(series)
        else:
            series_to_fit = series

        # Fit ARIMA model
        model = ARIMA(series, order=(self.p, self.d, self.q))
        self.model_fit = model.fit()

        self.fitted_values = self.model_fit.fittedvalues
        self.residuals = self.model_fit.resid

        print(self.model_fit.summary())
        return self.model_fit

    def check_residuals_autocorrelation(self, lags=20):
        """
        Check autocorrelation of residuals.
        Plot ACF and PACF of residuals.
        """
        if self.residuals is None:
            raise ValueError(
                "Fit the model before checking residual autocorrelation.")
        acf_vals = acf(self.residuals, nlags=lags)
        pacf_vals = pacf(self.residuals, nlags=lags)

        plt.figure(figsize=(12, 5))
        plt.subplot(121)
        plt.stem(range(lags+1), acf_vals, use_line_collection=True)
        plt.title("Residuals ACF")

        plt.subplot(122)
        plt.stem(range(lags+1), pacf_vals, use_line_collection=True)
        plt.title("Residuals PACF")

        plt.show()

    def forecast(self, steps=10):
        """
        Forecast future values for given number of steps.
        Returns forecasted values as a pandas Series.
        """
        if self.model_fit is None:
            raise ValueError("Fit the model before forecasting.")
        forecast_result = self.model_fit.get_forecast(steps=steps)
        forecast_series = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        return forecast_series, conf_int


if __name__ == "__main__":
    # Example usage
    import yfinance as yf

    # Download historical stock data for demonstration (e.g. Apple)
    data = yf.download("AAPL", start="2020-01-01", end="2023-01-01")
    close_prices = data['Close']

    # Instantiate ARIMA model example: ARIMA(1,1,1)
    arima_model = ARIMAModel(p=1, d=1, q=1)

    # Check stationarity
    stationary = arima_model.check_stationarity(close_prices)
    print(f"Series stationary? {stationary}")

    # Fit model
    arima_model.fit(close_prices)

    # Check residual autocorrelation
    arima_model.check_residuals_autocorrelation()

    # Forecast next 10 steps
    forecast, conf_int = arima_model.forecast(10)
    print("Forecasted prices:")
    print(forecast)

    # Plot forecast with confidence intervals
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(close_prices.index, close_prices, label='Historical')
    plt.plot(forecast.index, forecast, label='Forecast', color='red')
    plt.fill_between(
        forecast.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='pink', alpha=0.3)
    plt.legend()
    plt.show()
