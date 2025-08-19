<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Trade Jockey: Advanced Stock Analytics Platform

## Overview

**Trade Jockey** is a comprehensive, modular analytics platform designed for both retail and professional traders. It leverages modern **streamlit-based web UI**, high-performance Python backends, and robust statistical tools to provide actionable insights into stock volatility, trend strength, and market predictions. The platform is engineered for rapid, customizable analysis of equities data using cutting-edge quantitative finance techniques.

***

## Key Features

- **Interactive Dashboard:**
    - Intuitive navigation and clean layout, optimized for both desktop and tablet devices.
    - Sidebar-driven multi-page navigation: Home, All-Stocks, Compare-Stocks, Stocks.
- **Multi-Symbol Analysis:**
    - Compare metrics (volatility, ratios, ADX) across multiple stocks.
    - Dynamic period selection for advanced comparative studies.
- **Volatility Analytics:**
    - Raw and annualized historical volatility calculations.
    - Rolling window volatility visualization.
    - Volatility ratio comparisons over custom and preset periods.
- **Trend Strength Metrics:**
    - Average Directional Index (ADX), +DI, -DI calculations mimic professional trading platforms.
    - Slicing by custom and fixed periods.
- **ARIMA-based Market Predictions:**
    - Time-series forecasting module powered by Statsmodels and pmdarima.
    - Automated model diagnostics: stationarity checks, backtesting, and error metrics.
    - Out-of-the-box integration with Yahoo Finance for instant data retrieval.
- **Fast Data Loading \& Preprocessing:**
    - Automatic symbol and file detection.
    - CSV ingestion with robust data cleaning.

***

## File Structure

```
TradeJockey/
│
├── Frontend/
│   └── modules/
│       ├── page_config.py        # Streamlit page config
│       ├── sidebar.py            # Custom sidebar and navigation control
│       ├── plot.py               # Altair-powered chart plotting
│       ├── data_loading.py       # Utility: symbol/file discovery and loading
│       ├── calculations.py       # Core metric calculations: volatility, ratios, ADX
│       ├── ui_controls.py        # User input management (widgets, form controls)
│
├── Backend/
│   └── Strategy/
│       ├── volatility.py         # Historical/realized volatility functions
│       ├── adx.py                # ADX, +DI, -DI calculation logic
│       ├── arima.py              # ARIMA prediction & backtesting module
│       ├── __init__.py           # Strategy package loader
│
├── views/
│   ├── home.py                   # Home page rendering
│   ├── all_stocks.py             # Multi-stock analytics page
│   ├── compare.py                # Symbol comparison logic
│   ├── single.py                 # Single stock analytics view
│
├── market_prediction.ipynb       # End-to-end S&P 500 prediction notebook
├── Home.py                       # Main Streamlit entrypoint
```


***

## How It Works

### 1. **Data Onboarding**

- Drop your CSV files into the designated data folder.
- Platform auto-detects available symbols and periods.


### 2. **Custom Metric Visualization**

- Quickly plot rolling volatility, trend strength, and other metrics with adjustable periods.


### 3. **Comparative Analytics**

- Select multiple stocks for side-by-side metric tables―ideal for portfolio risk assessment.


### 4. **ARIMA Prediction Engine**

- Configure manual or auto ARIMA models for price forecasting.
- Backtest model accuracy directly in-app, visualize predictions vs. actuals.


### 5. **Export-Ready Charts \& Tables**

- All charts rendered via Altair for publication-ready outputs.
- Data tables are easily exportable for further analysis.

***

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/YOUR-REPO/TradeJockey.git
cd TradeJockey
```

2. **Install Python requirements:**

```bash
pip install -r requirements.txt
```

3. **Launch the Streamlit server:**

```bash
streamlit run Home.py
```

4. **Access the app in your browser at `localhost:8501`**

***

## Technologies Used

- **Python 3.8+**
- **streamlit:** UI/UX framework
- **NumPy, pandas:** Data manipulation
- **Altair:** Visualizations
- **Statsmodels, pmdarima:** ARIMA time series modeling
- **scikit-learn:** Evaluation metrics
- **Yahoo Finance API:** Data sourcing

***

## Customization \& Extensibility

Trade Jockey is architected for modular expansion. You can easily add new metrics, prediction algorithms, or data sources by extending backend modules and updating the frontend controls. Custom analysis periods, comparison tables, and indicator plots are highly configurable.

***

## Contributing

We welcome issues, ideas and PRs! Please ensure new code is well-documented and passes pre-commit linting, and submit pull requests with clear test cases.

***

## License

Distributed under the MIT License. See `LICENSE` for details.

***

Trade Jockey—empowering you with professional-grade analytics, forecast accuracy, and deep market insights for every trader’s journey.

<div style="text-align: center">⁂</div>

[^1]: init.py

[^2]: adx.py

[^3]: arima.py

[^4]: volatility.py

[^5]: market_prediction.ipynb

[^6]: Home.py

[^7]: calculations.py

[^8]: data_loading.py

[^9]: page_config.py

[^10]: plot.py

[^11]: sidebar.py

[^12]: ui_controls.py

