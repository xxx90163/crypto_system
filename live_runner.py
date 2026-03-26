import requests
import json
import time

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "SUIUSDT"]

def fetch_kline(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": "1m",
        "limit": 100
    }
    res = requests.get(url, params=params)
    data = res.json()

    result = []
    for k in data:
        result.append({
            "time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })
    return result

def run():
    while True:
        output = {}

        for symbol in SYMBOLS:
            print(f"fetching {symbol}...")
            output[symbol] = {
                "klines": fetch_kline(symbol)
            }

        with open("steelx_live.json", "w") as f:
            json.dump(output, f)

        print("🔥 已更新 steelx_live.json")

        time.sleep(30)  # 每30秒更新一次

if __name__ == "__main__":
    run()
