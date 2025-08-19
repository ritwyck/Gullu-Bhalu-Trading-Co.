import requests

FINNHUB_KEY = "d2i2vppr01qucbnmsn7gd2i2vppr01qucbnmsn80"


def get_symbols(query):
    url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_KEY}"
    data = requests.get(url).json()
    matches = data.get("result", [])[:5]
    return [(m.get("symbol", ""), m.get("description", "")) for m in matches]
