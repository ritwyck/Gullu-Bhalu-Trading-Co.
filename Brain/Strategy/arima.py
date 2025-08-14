import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
from pmdarima import auto_arima
import yfinance as yf


class ARIMAModel:
    def __init__(self, p=None, d=None, q=None):
        """
        Optionally set manual ARIMA order (p,d,q)
        """
        self.p = p
        self.d = d
        self.q = q
        self.model_fit = None
        self.auto_model_fit = None

    def check_stationarity(self, series, significance=0.05):
        result = adfuller(series.dropna())
        pvalue = result[1]
        print(f"ADF Test p-value: {pvalue:.5f}")
        return pvalue < significance

    def fit_manual(self, series):
        """
        Fit manual ARIMA(p,d,q) model.
        """
        if self.p is None or self.d is None or self.q is None:
            raise ValueError("Manual ARIMA order (p,d,q) must be specified.")
        model = ARIMA(series, order=(self.p, self.d, self.q))
        self.model_fit = model.fit()
        print(self.model_fit.summary())
        return self.model_fit

    def fit_auto(self, series, seasonal=False, m=1, max_p=5, max_q=5, max_d=2):
        """
        Auto-ARIMA model selection using pmdarima.
        """
        model_auto = auto_arima(
            series,
            start_p=0, start_q=0,
            max_p=max_p, max_q=max_q, max_d=max_d,
            seasonal=seasonal, m=m,
            trace=True, error_action='ignore', suppress_warnings=True, stepwise=True
        )
        self.auto_model_fit = model_auto
        print(f"Auto-selected order: {model_auto.order}")
        return model_auto

    def forecast(self, steps=10, use_auto=False):
        """
        Forecast next 'steps' with chosen model.
        """
        if use_auto and self.auto_model_fit is not None:
            forecast = self.auto_model_fit.predict(
                n_periods=steps, return_conf_int=True)
            forecast_vals, conf_int = forecast
            return pd.Series(forecast_vals), pd.DataFrame(conf_int)
        elif self.model_fit is not None:
            result = self.model_fit.get_forecast(steps=steps)
            forecast_vals = result.predicted_mean
            conf_int = result.conf_int()
            return forecast_vals, conf_int
        else:
            raise ValueError("No fitted model available.")

    def backtest(self, series, order=None, use_auto=False, test_size=0.2):
        """
        Backtest model on holdout (last test_size fraction).
        Returns metrics: MAE, RMSE, and plots predicted vs ground truth.
        """
        n = len(series)
        test_n = int(n * test_size)
        train, test = series[:-test_n], series[-test_n:]

        if use_auto:
            model_auto = self.fit_auto(train)
            preds = model_auto.predict(n_periods=len(test))
        else:
            if order:
                self.p, self.d, self.q = order
            self.fit_manual(train)
            result = self.model_fit.get_forecast(steps=len(test))
            preds = result.predicted_mean

        # Metrics
        mae = mean_absolute_error(test, preds)
        rmse = np.sqrt(mean_squared_error(test, preds))
        print(f"MAE: {mae:.4f} | RMSE: {rmse:.4f}")

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(test.index, test, label='Actual')
        plt.plot(test.index, preds, label='Predicted', color='red')
        plt.title("Backtest: Forecast vs Actual")
        plt.legend()
        plt.show()

        return {'mae': mae, 'rmse': rmse, 'preds': preds}


if __name__ == "__main__":

    data = yf.download("AAPL", start="2020-01-01", end="2023-01-01")
    series = data['Close'].dropna()

    arima_manual = ARIMAModel(p=1, d=1, q=1)
    print('\nChecking stationarity:')
    print(arima_manual.check_stationarity(series))

    print('\nManual ARIMA:')
    arima_manual.fit_manual(series)
    forecast, conf = arima_manual.forecast(10)
    print("\nManual Forecast:")
    print(forecast)

    print('\nAuto-ARIMA:')
    arima_auto = ARIMAModel()
    arima_auto.fit_auto(series)
    forecast_auto, conf_auto = arima_auto.forecast(10, use_auto=True)
    print("\nAuto-ARIMA Forecast:")
    print(forecast_auto)

    print('\nManual ARIMA Backtest:')
    arima_manual.backtest(series, order=(1, 1, 1), use_auto=False)
    print('\nAuto-ARIMA Backtest:')
    arima_auto.backtest(series, use_auto=True)
