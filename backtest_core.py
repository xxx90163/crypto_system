import requests
import pandas as pd
import numpy as np

# =========================
# 🔥 Binance Data
# =========================
def get_binance_data(symbol="BTCUSDT", interval="5m", limit=1000):

    url = "https://fapi.binance.com/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "_","_","_","_","_","_"
    ])

    df = df[["open","high","low","close","volume"]]
    df = df.astype(float)

    return df


# =========================
# 🔥 Liquidity Core（區間累積）
# =========================
def build_liquidity_map(df, window=50, bin_size=10):

    price_bins = {}

    for i in range(len(df)-window, len(df)):

        price = int(df.iloc[i]["close"] / bin_size) * bin_size

        strength = abs(df.iloc[i]["close"] - df.iloc[i]["open"]) * df.iloc[i]["volume"]

        price_bins[price] = price_bins.get(price, 0) + strength

    return price_bins


# =========================
# 🔥 Gravity（核心）
# =========================
def calc_gravity(price_bins, current_price):

    liq_above = sum(v for p, v in price_bins.items() if p > current_price)
    liq_below = sum(v for p, v in price_bins.items() if p <= current_price)

    total = liq_above + liq_below + 1e-6

    gravity = (liq_above - liq_below) / total

    return gravity, liq_above, liq_below


# =========================
# 🔥 Direction（強度過濾版）
# =========================
def get_direction(gravity):

    # 🔥 核心升級：只做強流動性
    if abs(gravity) < 0.2:
        return "SKIP"

    if gravity > 0:
        return "SHORT"
    else:
        return "LONG"


# =========================
# 🔥 TP Engine（簡化穩定版）
# =========================
def simulate_trade(df, i, direction):

    entry = df.iloc[i]["close"]

    for j in range(i+1, min(i+6, len(df))):

        row = df.iloc[j]

        if direction == "LONG":
            pnl = row["close"] - entry
        else:
            pnl = entry - row["close"]

        # TP
        if pnl > 1:
            return 1

        # SL
        if pnl < -1:
            return -1

    return 0


# =========================
# 🔥 Backtest
# =========================
def backtest(df):

    wins, losses, skips = 0, 0, 0
    results = []

    for i in range(60, len(df)-6):

        window_df = df.iloc[i-50:i]

        bins = build_liquidity_map(window_df)

        price = df.iloc[i]["close"]

        gravity, liq_above, liq_below = calc_gravity(bins, price)

        # 🔥 強度過濾（關鍵）
        if abs(gravity) < 0.2:
            skips += 1
            continue

        direction = "SHORT" if gravity > 0 else "LONG"

        pnl = simulate_trade(df, i, direction)

        results.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    print("\n🔥 Steel X CORE v2（Liquidity Filter）")
    print(f"total: {total}")
    print(f"wins: {wins}")
    print(f"losses: {losses}")
    print(f"skips: {skips}")
    print(f"win_rate: {round(wins/total,3) if total else 0}")
    print(f"avg_R: {round(np.mean(results),3) if results else 0}")


# =========================
# RUN
# =========================
if __name__ == "__main__":

    df = get_binance_data()

    backtest(df)
