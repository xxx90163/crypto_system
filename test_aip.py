# test_aip.py

import json

data = {
    "symbol": "BTCUSDT",
    "price": 70000,
    "liq_above": 500000000,
    "liq_below": 200000000,
    "oi": 85000000,
    "funding_rate": 0.01,
    "long_ratio": 0.6,
    "short_ratio": 0.4
}

# 存成 JSON 檔案
with open("output.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ AIP JSON 已輸出")
