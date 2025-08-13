# Stock Volatility Dashboard

## Overview

This is a Streamlit-based Stock Volatility Dashboard app that lets you analyze stock volatilities in two modes:

- **Single Stock**: View historical and realized volatilities for a selected stock over various periods and plot different stock metrics.
- **Compare Multiple Stocks**: Select 2 to 5 stocks to compare their historical volatilities side-by-side, with customizable rolling window and ratio metrics.

Users can switch between modes using the app’s mode selector.

---

## Dependencies

The app requires the following Python packages:

- **streamlit**: For the interactive web app interface.
- **pandas**: For data manipulation.
- **numpy**: For numerical calculations.
- **altair**: For interactive plotting charts.
- **Brain** (custom or third-party module): Provides volatility calculation utilities such as `load_data`, `historical_volatility`, `realized_volatility`.
- **FrontEnd** (local package/module): Contains UI components including `singleStockView` and `multiStockView` with main view functions.

---

## Installation

Assuming you have **Python 3.7+** installed, you can install the dependencies via pip:

```bash
pip install streamlit pandas numpy altair
```

For the **Brain** and **FrontEnd** modules, ensure they are in your Python path or installed in your environment if they are custom packages. They should include the necessary volatility calculation functions and UI view components.

---

## Running the App

1. **Project Structure Sample**

```
your-project/
│
├── Vault/
│   └── Historical_Stock_Data/         # Your CSV stock price data files here
│
├── FrontEnd/
│   ├── singleStockView.py             # Contains single_stock_view()
│   └── multiStockView.py              # Contains compare_stocks_view()
│
├── Brain/
│   └── volatility.py                  # Contains load_data(), realized_volatility(), historical_volatility() etc.
│
└── Launcher.py                       # Main launcher file (Streamlit entry point)
```

2. **Run via the launcher script**

From your terminal, inside the project folder, run:

```bash
streamlit run Launcher.py
```

3. **Using the App**

- The app title will display "📊 Stock Volatility Dashboard".
- Use the mode radio button at the top to switch between:
  - **Single Stock**: Choose a stock symbol, view historical volatility data in a table with ratio columns, select metric and rolling window, and visualize.
  - **Compare Multiple Stocks**: Select 2–5 stock symbols, specify volatility and ratio periods; compare volatility tables side-by-side for all selected stocks; visualize selected metrics comparatively.

All volatility data is based on historical price data CSV files stored in the `Vault/Historical_Stock_Data` folder.

---

## Summary

- **Dependencies**: Install via pip — `streamlit`, `pandas`, `numpy`, `altair`.
- **Data**: Place historical stock CSV files into `Vault/Historical_Stock_Data`.
- **Modules**: Make sure `Brain` and `FrontEnd` are accessible Python packages or modules.
- **Run**: Launch the app using `streamlit run Launcher.py`.
- **Use**: Interactively explore volatility measures by selecting stock(s), periods, and metrics.

---

Please reach out if you need guidance on setting up the `Brain` or `FrontEnd` modules, or help with adding new features or deployments!
