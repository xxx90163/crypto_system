import pandas as pd
import numpy as np
import requests
import json
import os
import time

# =========================
# CONFIG
# =========================
USE_REAL_DATA = False
CACHE_FILE = "liq_cache.json"
CACHE_TTL = 60  # 秒（避免一直打 API）

# =========================
# CACHE SYSTEM
# =========================
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_cached_liq():
    cache = load_cache()

    now = time.time()

    if "timestamp" in cache:
        if now - cache["timestamp"] < CACHE_TTL:
            return cache.get("liq_above"), cache.get("liq_below"), "CACHE"

    return None, None, None


def update_cache(liq_above, liq_below):
    cache = {
        "liq_above": liq_above,
        "liq_below": liq_below,
        "timestamp": time.time()
    }
    save_cache(cache)


# =========================
# API FETCH（安全版）
# =========================
def fetch_liquidation():
    try:
        url = "https://open-api-v4.coinglass.com/api/futures/liquidation/history"
        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            data = r.json().get("data", [])

            if data:
                liq_above = sum(x.get("longLiquidationUsd", 0) for x in data)
                liq_below = sum(x.get("shortLiquidationUsd", 0) for x in data)

                update_cache(liq_above, liq_below)

                return liq_above, liq_below, "REAL"

    except:
        pass

    return None, None, None


# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# LIQUIDITY ENGINE（V54）
# =========================
def calc_liquidity(row):

    if USE_REAL_DATA:

        # 1️⃣ 先拿 cache
        liq_above, liq_below, mode = get_cached_liq()

        if liq_above is not None:
            return liq_above, liq_below, mode

        # 2️⃣ 再打 API
        liq_above, liq_below, mode = fetch_liquidation()

        if liq_above is not None:
            return liq_above, liq_below, mode

    # =====================
    # fallback proxy
    # =====================
    high = safe_get(row, "high")
    low = safe_get(row, "low")
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    volume = safe_get(row, "volume", 1)

    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    liq_above = upper_wick * volume
    liq_below = lower_wick * volume

    return liq_above, liq_below, "PROXY"


# =========================
# REGIME
# =========================
def get_regime(row):
    if "regime" in row:
        return row["regime"]

    return "TREND" if safe_get(row, "close") > safe_get(row, "open") else "RANGE"


# =========================
# SIGNAL
# =========================
def generate_signal(row):
    return "LONG" if get_regime(row) == "TREND" else "SHORT"


# =========================
# FILTER（升級版）
# =========================
def liquidity_filter(liq_above, liq_below):

    total = liq_above + liq_below

    if total == 0:
        return False, 0

    imbalance = abs(liq_above - liq_below) / total

    # 🔥 動態門檻
    threshold = 0.25 if total > 1000 else 0.15

    if imbalance < threshold:
        return False, imbalance

    return True, imbalance


# =========================
# BACKTEST（Streaming 模式）
# =========================
def backtest(df):

    wins, losses, skips = 0, 0, 0
    pnl_list = []

    for _, row in df.iterrows():

        liq_above, liq_below, mode = calc_liquidity(row)

        allow, score = liquidity_filter(liq_above, liq_below)

        if not allow:
            skips += 1
            continue

        signal = generate_signal(row)

        move = np.random.choice([-80, 150])
        pnl = move if signal == "LONG" else -move

        pnl_list.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "skips": skips,
        "win_rate": round(wins / total, 3) if total else 0,
        "avg_pnl": round(np.mean(pnl_list), 2) if pnl_list else 0
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":

    df = pd.DataFrame({
        "open": np.random.rand(1000) * 100,
        "close": np.random.rand(1000) * 100,
        "high": np.random.rand(1000) * 100,
        "low": np.random.rand(1000) * 100,
        "volume": np.random.rand(1000) * 1000
    })

    result = backtest(df)

    print("🔥 Steel X V54 (Streaming Liquidity Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
