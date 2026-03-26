# test_aip.py

import requests
import json

# 這部分是從 Binance 抓取真實價格
def fetch_price():
    url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    price = float(data["price"])
    return price

# 模擬的 AIP 配置資料
data = {
    'symbol': 'BTCUSDT',
    'price': 70000,  # 這裡稍後會被抓取的價格替代
    'liq_above': 50000000,
    'liq_below': 20000000,
    'oi': 85000000,
    'funding_rate': 0.01,
    'long_ratio': 0.6,
    'short_ratio': 0.4
}

# 抓取 BTC 目前價格
current_price = fetch_price()

# 更新資料中的價格
data['price'] = current_price

# 顯示結果
print("✅ Steel X AIP 結果:")
print(json.dumps(data, indent=4))