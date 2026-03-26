# ================================
# 🔥 Steel X V64.2（Multi-Bar TP Engine）
# 修正 TP 無法觸發問題
# ================================

import pandas as pd


# ================================
# 1️⃣ Regime
# ================================
def detect_regime(row):

    body = abs(row["close"] - row["open"])
    range_ = row["high"] - row["low"]

    if range_ == 0:
        return "CHOP"

    strength = body / range_

    if strength > 0.6:
        return "TREND"
    elif strength < 0.3:
        return "CHOP"
    else:
        return "RANGE"


# ================================
# 2️⃣ Liquidity
# ================================
def calc_liquidity(row):

    upper_wick = row["high"] - max(row["open"], row["close"])
    lower_wick = min(row["open"], row["close"]) - row["low"]

    vol = row.get("volume", 1)

    liq_above = upper_wick * vol
    liq_below = lower_wick * vol

    return liq_above, liq_below


# ================================
# 3️⃣ Score
# ================================
def calc_score(row, liq_above, liq_below):

    score = 0

    if liq_below > liq_above:
        score += 1
    else:
        score -= 1

    if row["close"] > row["open"]:
        score += 1
    else:
        score -= 1

    return score


# ================================
# 4️⃣ Router
# ================================
def router(score, imbalance, regime):

    if abs(score) < 2:
        return "SKIP"

    if regime == "TREND":
        score += 0.5

    if regime == "CHOP":
        return "SKIP"

    if score >= 2 and imbalance > 0:
        return "LONG"

    if score <= -2 and imbalance < 0:
        return "SHORT"

    return "SKIP"


# ================================
# 5️⃣ 🔥 Multi-Bar TP Engine
# ================================
def simulate_trade(df, i, direction):

    entry = df.iloc[i]["close"]

    tp1 = 0.3
    tp2 = 0.8
    sl  = -0.7

    max_lookahead = 5  # 🔥 核心

    for j in range(i + 1, min(i + 1 + max_lookahead, len(df))):

        row = df.iloc[j]

        if direction == "LONG":

            move = row["high"] - entry
            drawdown = row["low"] - entry

        else:

            move = entry - row["low"]
            drawdown = entry - row["high"]

        # SL
        if drawdown <= sl:
            return sl

        # TP2
        if move >= tp2:
            return 0.3 + 0.8

        # TP1
        if move >= tp1:
            return tp1

    # 沒 hit → 小收
    return move * 0.5


# ================================
# 6️⃣ Backtest
# ================================
def backtest(df):

    wins = 0
    losses = 0
    skips = 0

    results = []

    for i in range(len(df) - 6):

        row = df.iloc[i]

        regime = detect_regime(row)

        liq_above, liq_below = calc_liquidity(row)

        score = calc_score(row, liq_above, liq_below)

        imbalance = liq_below - liq_above

        decision = router(score, imbalance, regime)

        if decision == "SKIP":
            skips += 1
            continue

        pnl = simulate_trade(df, i, decision)

        results.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    win_rate = wins / total if total > 0 else 0
    avg_R = sum(results) / len(results) if results else 0

    print("🔥 Steel X V64.2 (Multi-Bar TP)")
    print(f"total: {total}")
    print(f"wins: {wins}")
    print(f"losses: {losses}")
    print(f"skips: {skips}")
    print(f"win_rate: {round(win_rate, 3)}")
    print(f"avg_R: {round(avg_R, 3)}")


# ================================
# 7️⃣ Run
# ================================
if __name__ == "__main__":

    df = pd.read_csv("data.csv")

    backtest(df)
