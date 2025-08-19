from datetime import datetime, timedelta


def fetch_historical_data(symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_date.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    return hist
