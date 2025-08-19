import requests
import pandas as pd

all_data = []
page = 1

while True:
    url = f"https://stockanalysis.com/api/screener/s/i/?m=all&page={page}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    data = r.json()

    # Check if data exists
    if not data["data"]:
        break

    df = pd.json_normalize(data["data"])
    all_data.append(df)

    print(f"Fetched page {page}, rows: {len(df)}")
    page += 1

# Combine all
final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv("indonesia_stocks_full.csv", index=False)

print("✅ Saved", len(final_df), "rows to indonesia_stocks_full.csv")
