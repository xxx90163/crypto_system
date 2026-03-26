import requests
import json
import time

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "SUIUSDT"]

def fetch_kline(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": "1m",
        "limit": 200
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

def build_live():
    output = {}

    for symbol in SYMBOLS:
        print(f"fetching {symbol}...")
        kline = fetch_kline(symbol)

        output[symbol] = {
            "klines": kline
        }

    with open("steelx_live.json", "w") as f:
        json.dump(output, f)

    print("🔥 steelx_live.json 已生成")

if __name__ == "__main__":
    build_live()
