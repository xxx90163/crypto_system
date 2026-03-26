import requests
import pandas as pd
import time
import os

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","DOGEUSDT","SUIUSDT"]

BASE_DIR = "datahub"
os.makedirs(BASE_DIR, exist_ok=True)


# =========================
# 🔥 KLINE
# =========================
def fetch_kline(symbol):

    url = "https://fapi.binance.com/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 200
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

    params = {"symbol": symbol}

    data = requests.get(url, params=params).json()

    return float(data["openInterest"])


# =========================
# 🔥 FUNDING
# =========================
def fetch_funding(symbol):

    url = "https://fapi.binance.com/fapi/v1/premiumIndex"

    params = {"symbol": symbol}

    data = requests.get(url, params=params).json()

    return float(data["lastFundingRate"])


# =========================
# 🔥 保存
# =========================
def save(symbol, df, oi, funding):

    file = f"{BASE_DIR}/{symbol}.csv"

    df["oi"] = oi
    df["funding"] = funding

    df.to_csv(file, index=False)


# =========================
# 🔥 主流程
# =========================
def run():

    print("🔥 Steel X DataHub Running...")

    for symbol in SYMBOLS:

        try:
            df = fetch_kline(symbol)
            oi = fetch_oi(symbol)
            funding = fetch_funding(symbol)

            save(symbol, df, oi, funding)

            print(f"✅ {symbol} updated")

        except Exception as e:
            print(f"❌ {symbol} error:", e)


if __name__ == "__main__":
    run()
