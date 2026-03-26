import requests
import pandas as pd
import time
import json
import os

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","DOGEUSDT","SUIUSDT"]

OUTPUT_FILE = "steelx_live.json"


# =========================
# 🔥 KLINE
# =========================
def fetch_kline(symbol):

    url = "https://fapi.binance.com/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 100
    }

    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "_","_","_","_","_","_"
    ])

    df = df[["time","open","high","low","close","volume"]]
    df = df.astype(float)

    return df


# =========================
# 🔥 OI
# =========================
def fetch_oi(symbol):

    url = "https://fapi.binance.com/fapi/v1/openInterest"
    return float(requests.get(url, params={"symbol": symbol}).json()["openInterest"])


# =========================
# 🔥 FUNDING
# =========================
def fetch_funding(symbol):

    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    return float(requests.get(url, params={"symbol": symbol}).json()["lastFundingRate"])


# =========================
# 🔥 組裝資料
# =========================
def build_payload():

    payload = {}

    for symbol in SYMBOLS:

        try:
            df = fetch_kline(symbol)

            payload[symbol] = {
                "price": df.iloc[-1]["close"],
                "volume": df.iloc[-1]["volume"],
                "oi": fetch_oi(symbol),
                "funding": fetch_funding(symbol),
                "recent": df.tail(50).to_dict(orient="records")
            }

            print(f"✅ {symbol}")

        except Exception as e:
            print(f"❌ {symbol}", e)

    return payload


# =========================
# 🔥 存 JSON
# =========================
def save(payload):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)


# =========================
# 🔥 主程式（每分鐘更新）
# =========================
if __name__ == "__main__":

    print("🔥 Steel X Live DataHub Started")

    while True:

        payload = build_payload()
        save(payload)

        print("🚀 Updated\n")

        time.sleep(60)
