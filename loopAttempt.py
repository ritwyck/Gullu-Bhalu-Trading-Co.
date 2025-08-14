import yfinance as yf
import time


def fetch_indian_stock_minute_data(stock_symbol="RELIANCE.NS", period="7d", interval="1m"):
    ticker = yf.Ticker(stock_symbol)
    df = ticker.history(period=period, interval=interval)
    return df


if __name__ == "__main__":
    while True:
        data = fetch_indian_stock_minute_data()
        # Print the most recent 5 one-minute bars
        print(data.tail(5))
        print("\n--- Updated at", time.strftime("%Y-%m-%d %H:%M:%S"), "---\n")
        time.sleep(60)  # wait one minute before updating again
