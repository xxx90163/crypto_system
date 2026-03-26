import requests
import json
import time
import random

SYMBOL = "BTCUSDT"

# =========================
# 1️⃣ KLINES（價格）
# =========================
def fetch_klines(symbol=SYMBOL, interval="1m", limit=100):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    data = requests.get(url, params=params).json()

    klines = []
    for k in data:
        klines.append({
            "time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })
    return klines


# =========================
# 2️⃣ OI（未平倉量）
# =========================
def fetch_oi(symbol=SYMBOL):
    url = "https://fapi.binance.com/fapi/v1/openInterest"
    params = {"symbol": symbol}
    data = requests.get(url, params=params).json()

    return {
        "open_interest": float(data["openInterest"]),
        "time": data["time"]
    }


# =========================
# 3️⃣ Funding
# =========================
def fetch_funding(symbol=SYMBOL):
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    params = {"symbol": symbol}
    data = requests.get(url, params=params).json()

    return {
        "funding_rate": float(data["lastFundingRate"]),
        "mark_price": float(data["markPrice"]),
        "index_price": float(data["indexPrice"])
    }


# =========================
# 4️⃣ Orderbook
# =========================
def fetch_orderbook(symbol=SYMBOL):
    url = "https://fapi.binance.com/fapi/v1/depth"
    params = {
        "symbol": symbol,
        "limit": 50
    }
    data = requests.get(url, params=params).json()

    bids = data["bids"]
    asks = data["asks"]

    bid_volume = sum(float(b[1]) for b in bids)
    ask_volume = sum(float(a[1]) for a in asks)

    return {
        "bid_volume": bid_volume,
        "ask_volume": ask_volume,
        "imbalance": bid_volume / (ask_volume + 1e-6)
    }


# =========================
# 5️⃣ Liquidation（暫用 Proxy）
# =========================
def fetch_liquidation_proxy():
    return {
        "liq_above": random.uniform(1_000_000, 5_000_000),
        "liq_below": random.uniform(1_000_000, 5_000_000)
    }


# =========================
# 🔥 主整合
# =========================
def build_data():
    try:
        klines = fetch_klines()
        oi = fetch_oi()
        funding = fetch_funding()
        orderbook = fetch_orderbook()
        liquidation = fetch_liquidation_proxy()

        data = {
            "BTCUSDT": {
                "klines": klines,
                "oi": oi,
                "funding": funding,
                "orderbook": orderbook,
                "liquidation": liquidation,
                "timestamp": int(time.time() * 1000)
            }
        }

        return data

    except Exception as e:
        print("❌ Error:", e)
        return None


# =========================
# 💾 存檔
# =========================
def save_json(data):
    with open("steelx_live.json", "w", encoding="utf-8") as f:
        json.dump(data, f)


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    print("🚀 Running Steel X Data Gateway...")

    data = build_data()

    if data:
        save_json(data)
        print("✅ steelx_live.json updated")
    else:
        print("❌ Failed to build data")
