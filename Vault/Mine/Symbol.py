import yfinance as yf
import os

nifty_100_symbols = [
    "ABB",
    "ADANIENSOL",
    "ADANIENT",
    "ADANIGREEN",
    "ADANIPORTS",
    "ADANIPOWER",
    "AMBUJACEM",
    "APOLLOHOSP",
    "ASIANPAINT",
    "DMART",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BAJAJHLDNG",
    "BAJAJHFL",
    "BANKBARODA",
    "BEL",
    "BPCL",
    "BHARTIARTL",
    "BOSCHLTD",
    "BRITANNIA",
    "CGPOWER",
    "CANBK",
    "CHOLAFIN",
    "CIPLA",
    "COALINDIA",
    "DLF",
    "DABUR",
    "DIVISLAB",
    "DRREDDY",
    "EICHERMOT",
    "ETERNAL",
    "GAIL",
    "GODREJCP",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFCLIFE",
    "HAVELLS",
    "HEROMOTOCO",
    "HINDALCO",
    "HAL",
    "HINDUNILVR",
    "HYUNDAI",
    "ICICIBANK",
    "ICICIGI",
    "ICICIPRULI",
    "ITC",
    "INDHOTEL",
    "IOC",
    "IRFC",
    "INDUSINDBK",
    "NAUKRI",
    "INFY",
    "INDIGO",
    "JSWENERGY",
    "JSWSTEEL",
    "JINDALSTEL",
    "JIOFIN",
    "KOTAKBANK",
    "LTIM",
    "LT",
    "LICI",
    "LODHA",
    "M&M",
    "MARUTI",
    "NTPC",
    "NESTLEIND",
    "ONGC",
    "PIDILITIND",
    "PFC",
    "POWERGRID",
    "PNB",
    "RECLTD",
    "RELIANCE",
    "SBILIFE",
    "MOTHERSON",
    "SHREECEM",
    "SHRIRAMFIN",
    "SIEMENS",
    "SBIN",
    "SUNPHARMA",
    "SWIGGY",
    "TVSMOTOR",
    "TCS",
    "TATACONSUM",
    "TATAMOTORS",
    "TATAPOWER",
    "TATASTEEL",
    "TECHM",
    "TITAN",
    "TORNTPHARM",
    "TRENT",
    "ULTRACEMCO",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZYDUSLIFE"
]

os.makedirs("Vault/Historical_Stock_Data", exist_ok=True)

for symbol in nifty_100_symbols:
    try:
        nse_symbol = symbol + ".NS"  # For NSE data
        ticker = yf.Ticker(nse_symbol)
        info = ticker.info
        company_name = info.get('longName', 'UnknownCompany').replace(" ", "_")

        hist = ticker.history(period='6mo')
        df = hist[['Open', 'High', 'Low', 'Close']].reset_index()

        filename = f"Vault/Historical_Stock_Data/{symbol}.csv"
        df.to_csv(filename, index=False)

        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
