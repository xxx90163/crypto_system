import pandas as pd
import numpy as np

TP = 150
SL = -80

# 🔥 門檻
LIQ_THRESHOLD = 1.5

# =========================
# Regime
# =========================
def get_regime(row):
    if row["close"] > row["ema_50"]:
        return "TREND"
    else:
        return "RANGE"

# =========================
# 🔥 強化 Liquidity Proxy
# =========================
def calc_liquidity(row):

    body = abs(row["close"] - row["open"])
    full_range = row["high"] - row["low"]

    upper_wick = row["high"] - max(row["open"], row["close"])
    lower_wick = min(row["open"], row["close"]) - row["low"]

    # 👉 volume 容錯
    volume = row["volume"] if "volume" in row else 1

    # 🔥 核心：三層 proxy
    liq_above = (upper_wick + full_range * 0.3) * volume
    liq_below = (lower_wick + full_range * 0.3) * volume

    # 🔥 強度（加入波動）
    volatility_boost = full_range / (row["close"] + 1e-9)

    liq_strength = abs(liq_above - liq_below) * (1 + volatility_boost)

    return liq_above, liq_below, liq_strength

# =========================
# 🔥 強化 Sweep
# =========================
def detect_sweep(liq_above, liq_below, row):

    range_size = row["high"] - row["low"]

    if range_size == 0:
        return "NONE"

    # 👉 更嚴格
    if liq_above > liq_below * 1.5:
        return "SWEEP_UP"
    elif liq_below > liq_above * 1.5:
        return "SWEEP_DOWN"
    else:
        return "NONE"

# =========================
# 🔥 強化 Trap
# =========================
def trap_filter(row):

    body = abs(row["close"] - row["open"])
    full = row["high"] - row["low"]

    if full == 0:
        return False

    body_ratio = body / full

    # 🔥 強化條件
    if body_ratio < 0.25:
        return True

    return False

# =========================
# 🔥 Score（微調）
# =========================
def calc_score(row):

    score = 0

    # Regime
    if row["regime"] == "TREND":
        score += 2
    else:
        score -= 1

    # Momentum
    if row["close"] > row["ema_20"]:
        score += 1
    else:
        score -= 1

    # Sweep（加權）
    if row["sweep"] == "SWEEP_UP":
        score += 3
    elif row["sweep"] == "SWEEP_DOWN":
        score -= 3

    # Trap（更重）
    if row["trap"]:
        score -= 3

    return score

# =========================
# Entry
# =========================
def get_signal(score):
    if score >= 3:
        return "LONG"
    elif score <= -3:
        return "SHORT"
    else:
        return "SKIP"

# =========================
# Backtest
# =========================
def backtest(df):

    results = []

    for i in range(50, len(df)-1):

        row = df.iloc[i]

        regime = get_regime(row)

        liq_above, liq_below, liq_strength = calc_liquidity(row)

        # 🔥 核心：過濾
        if liq_strength < LIQ_THRESHOLD:
            results.append(0)
            continue

        sweep = detect_sweep(liq_above, liq_below, row)
        trap = trap_filter(row)

        row_data = {
            "regime": regime,
            "close": row["close"],
            "ema_20": row["ema_20"],
            "sweep": sweep,
            "trap": trap
        }

        score = calc_score(row_data)
        signal = get_signal(score)

        if signal == "SKIP":
            results.append(0)
            continue

        entry = df.iloc[i+1]["open"]
        future = df.iloc[i+1:i+6]

        pnl = 0

        for _, f in future.iterrows():

            if signal == "LONG":
                if f["high"] - entry >= TP:
                    pnl = TP
                    break
                elif f["low"] - entry <= SL:
                    pnl = SL
                    break

            elif signal == "SHORT":
                if entry - f["low"] >= TP:
                    pnl = TP
                    break
                elif entry - f["high"] <= SL:
                    pnl = SL
                    break

        results.append(pnl)

    return results

# =========================
# 主程式
# =========================
if __name__ == "__main__":

    df = pd.read_csv("data.csv")

    df["ema_20"] = df["close"].ewm(span=20).mean()
    df["ema_50"] = df["close"].ewm(span=50).mean()

    results = backtest(df)

    total = len(results)
    wins = sum(1 for r in results if r > 0)
    losses = sum(1 for r in results if r < 0)
    skips = sum(1 for r in results if r == 0)

    avg_pnl = np.mean(results) if results else 0

    print("\n🔥 Steel X V51.5 (Enhanced Liquidity Proxy)")
    print(f"total: {total}")
    print(f"wins: {wins}")
    print(f"losses: {losses}")
    print(f"skips: {skips}")
    print(f"win_rate: {wins / total:.3f}")
    print(f"avg_pnl: {avg_pnl:.2f}")
