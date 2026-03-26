import pandas as pd
import numpy as np

TP = 150
SL = -80

# =========================
# Regime
# =========================
def get_regime(row):
    if row["close"] > row["ema_50"]:
        return "TREND"
    else:
        return "RANGE"

# =========================
# 🔥 Liquidity（容錯版）
# =========================
def calc_liquidity(row):

    upper_wick = row["high"] - max(row["open"], row["close"])
    lower_wick = min(row["open"], row["close"]) - row["low"]

    # 👉 如果沒有 volume → 用 1 代替
    volume = row["volume"] if "volume" in row else 1

    liq_above = upper_wick * volume
    liq_below = lower_wick * volume

    return liq_above, liq_below

# =========================
# Sweep
# =========================
def detect_sweep(liq_above, liq_below):
    if liq_above > liq_below * 1.2:
        return "SWEEP_UP"
    elif liq_below > liq_above * 1.2:
        return "SWEEP_DOWN"
    else:
        return "NONE"

# =========================
# Trap
# =========================
def trap_filter(row):
    body = abs(row["close"] - row["open"])
    full = row["high"] - row["low"]

    if full == 0:
        return False

    return (body / full) < 0.3

# =========================
# Score
# =========================
def calc_score(row):

    score = 0

    if row["regime"] == "TREND":
        score += 2
    else:
        score -= 1

    if row["close"] > row["ema_20"]:
        score += 1
    else:
        score -= 1

    if row["sweep"] == "SWEEP_UP":
        score += 2
    elif row["sweep"] == "SWEEP_DOWN":
        score -= 2

    if row["trap"]:
        score -= 2

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
        liq_above, liq_below = calc_liquidity(row)
        sweep = detect_sweep(liq_above, liq_below)
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

    print("\n🔥 Steel X V50.1 (Liquidity Engine FIX)")
    print(f"total: {total}")
    print(f"wins: {wins}")
    print(f"losses: {losses}")
    print(f"skips: {skips}")
    print(f"win_rate: {wins / total:.3f}")
    print(f"avg_pnl: {avg_pnl:.2f}")
