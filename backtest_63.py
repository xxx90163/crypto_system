# ================================
# 🔥 Steel X V63.1（Router FIX）
# score 主導 / regime 輔助
# ================================

import pandas as pd


# ================================
# 1️⃣ Regime 判斷（簡單版）
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
# 2️⃣ Liquidity Proxy（強化版）
# ================================
def calc_liquidity(row):

    upper_wick = row["high"] - max(row["open"], row["close"])
    lower_wick = min(row["open"], row["close"]) - row["low"]

    vol = row.get("volume", 1)

    liq_above = upper_wick * vol
    liq_below = lower_wick * vol

    return liq_above, liq_below


# ================================
# 3️⃣ Score Engine
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
# 4️⃣ Router FIX（🔥核心）
# ================================
def router(score, imbalance, regime):

    # 基本品質過濾
    if abs(score) < 2:
        return "SKIP"

    # =====================
    # 👉 Regime 只做權重（不決定方向）
    # =====================
    if regime == "TREND":
        score += 0.5

    if regime == "CHOP":
        return "SKIP"

    # =====================
    # 👉 方向由 score 決定
    # =====================
    if score >= 2 and imbalance > 0:
        return "LONG"

    if score <= -2 and imbalance < 0:
        return "SHORT"

    return "SKIP"


# ================================
# 5️⃣ Backtest
# ================================
def backtest(df):

    wins = 0
    losses = 0
    skips = 0

    results = []

    for i in range(len(df) - 1):

        row = df.iloc[i]
        next_row = df.iloc[i + 1]

        regime = detect_regime(row)

        liq_above, liq_below = calc_liquidity(row)

        score = calc_score(row, liq_above, liq_below)

        imbalance = liq_below - liq_above

        decision = router(score, imbalance, regime)

        if decision == "SKIP":
            skips += 1
            continue

        # =====================
        # 👉 簡單PnL
        # =====================
        if decision == "LONG":
            pnl = next_row["close"] - row["close"]
        else:
            pnl = row["close"] - next_row["close"]

        results.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    win_rate = wins / total if total > 0 else 0
    avg_pnl = sum(results) / len(results) if results else 0

    print("🔥 Steel X V63.1 (Router FIX)")
    print(f"total: {total}")
    print(f"wins: {wins}")
    print(f"losses: {losses}")
    print(f"skips: {skips}")
    print(f"win_rate: {round(win_rate, 3)}")
    print(f"avg_pnl: {round(avg_pnl, 3)}")


# ================================
# 6️⃣ Run
# ================================
if __name__ == "__main__":

    df = pd.read_csv("data.csv")

    backtest(df)
