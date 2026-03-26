import requests
import pandas as pd

symbol = "BTCUSDT"
interval = "5m"
limit = 1000  # 👉 這裡就是K線數量（可改2000）

url = "https://fapi.binance.com/fapi/v1/klines"

params = {
    "symbol": symbol,
    "interval": interval,
    "limit": limit
}

response = requests.get(url, params=params)
data = response.json()

rows = []
for k in data:
    rows.append({
        "open": float(k[1]),
        "high": float(k[2]),
        "low": float(k[3]),
        "close": float(k[4])
    })

df = pd.DataFrame(rows)

df.to_csv("data.csv", index=False)

print("✅ data.csv 已生成（", len(df), "筆K線）")
