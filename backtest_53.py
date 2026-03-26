import pandas as pd
import numpy as np
import requests

# =========================
# CONFIG
# =========================
USE_REAL_DATA = False  # 👉 有 API 再改 True
CG_API_KEY = ""        # 👉 放你的 CoinGlass Key


# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# REAL DATA FETCH
# =========================
def fetch_liquidation(symbol="BTCUSDT"):
    try:
        url = "https://open-api-v4.coinglass.com/api/futures/liquidation/history"
        headers = {"CG-API-KEY": CG_API_KEY}
        params = {"symbol": symbol}

        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json().get("data", [])

            if data:
                liq_above = sum([x.get("longLiquidationUsd", 0) for x in data])
                liq_below = sum([x.get("shortLiquidationUsd", 0) for x in data])
                return liq_above, liq_below

    except:
        pass

    return None, None


def fetch_oi(symbol="BTCUSDT"):
    try:
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {"symbol": symbol}
        r = requests.get(url, params=params, timeout=5)

        if r.status_code == 200:
            return float(r.json()["openInterest"])
    except:
        pass

    return None


def fetch_funding(symbol="BTCUSDT"):
    try:
        url = "https://fapi.binance.com/fapi/v1/premiumIndex"
        params = {"symbol": symbol}
        r = requests.get(url, params=params, timeout=5)

        if r.status_code == 200:
            return float(r.json()["lastFundingRate"])
    except:
        pass

    return None


# =========================
# LIQUIDITY ENGINE
# =========================
def calc_liquidity(row):

    # =====================
    # REAL DATA
    # =====================
    if USE_REAL_DATA:
        liq_above, liq_below = fetch_liquidation()

        if liq_above is not None:
            return liq_above, liq_below, "REAL"

    # =====================
    # PROXY
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

    if safe_get(row, "close") > safe_get(row, "open"):
        return "TREND"
    return "RANGE"


# =========================
# SIGNAL
# =========================
def generate_signal(row):
    return "LONG" if get_regime(row) == "TREND" else "SHORT"


# =========================
# LIQUIDITY FILTER（升級）
# =========================
def liquidity_filter(liq_above, liq_below):

    total = liq_above + liq_below

    if total == 0:
        return False, 0

    imbalance = abs(liq_above - liq_below) / total

    # 👉 核心門檻（重要）
    if imbalance < 0.2:
        return False, imbalance

    return True, imbalance


# =========================
# BACKTEST
# =========================
def backtest(df):

    wins = 0
    losses = 0
    skips = 0
    pnl_list = []

    for _, row in df.iterrows():

        liq_above, liq_below, mode = calc_liquidity(row)

        allow, score = liquidity_filter(liq_above, liq_below)

        if not allow:
            skips += 1
            continue

        signal = generate_signal(row)

        # ===== PNL 模擬 =====
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

    print("🔥 Steel X V53 (Real Data Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
