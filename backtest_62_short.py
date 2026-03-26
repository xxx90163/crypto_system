import pandas as pd

def detect_regime(row):
    body = abs(row["close"] - row["open"])
    range_ = row["high"] - row["low"]

    if range_ == 0:
        return "CHOP", 0

    ratio = body / range_

    if ratio > 0.6:
        return "TREND", ratio
    elif ratio < 0.2:
        return "CHOP", ratio
    else:
        return "RANGE", ratio

def calc_liquidity(row):
    high, low = row["high"], row["low"]
    open_, close = row["open"], row["close"]

    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    total = upper_wick + lower_wick + 1e-6
    imbalance = (lower_wick - upper_wick) / total

    return imbalance

def break_structure(row):
    if row["close"] > row["open"]:
        return "UP"
    elif row["close"] < row["open"]:
        return "DOWN"
    return "NONE"

def trigger_score(row):

    regime, _ = detect_regime(row)
    imbalance = calc_liquidity(row)
    structure = break_structure(row)

    open_ = row["open"]
    close = row["close"]
    high = row["high"]
    low = row["low"]

    body = abs(close - open_)
    range_ = high - low

    if range_ == 0:
        return 0, regime, imbalance

    body_ratio = body / range_

    score = 0

    # SHORT 加分
    if imbalance < -0.3:
        score -= 1

    if structure == "DOWN":
        score -= 1

    # Trap
    trap = False

    if (close - low) > body * 1.5:
        trap = True

    if body_ratio < 0.2:
        trap = True

    if trap:
        score += 2

    if regime == "CHOP":
        score = 0

    return score, regime, imbalance

# =========================
# SHORT Decision
# =========================
def get_short_signal(score, imbalance, regime):

    if regime == "TREND":
        if score <= -2 and imbalance < 0:
            return True

    if regime == "RANGE":
        if score <= -2 and imbalance < 0:
            return True

    return False

# =========================
# Backtest
# =========================
def backtest(df):

    wins, losses, skips = 0, 0, 0
    total = 0
    R_total = 0

    for i in range(len(df)-1):

        row = df.iloc[i]
        next_row = df.iloc[i+1]

        score, regime, imbalance = trigger_score(row)

        if not get_short_signal(score, imbalance, regime):
            skips += 1
            continue

        entry = row["close"]
        exit_ = next_row["close"]

        pnl = entry - exit_

        if pnl > 0:
            wins += 1
            R_total += 1
        else:
            losses += 1
            R_total -= 1

        total += 1

    win_rate = wins / total if total else 0
    avg_R = R_total / total if total else 0

    print("🔥 V62 SHORT ENGINE")
    print("total:", total)
    print("wins:", wins)
    print("losses:", losses)
    print("skips:", skips)
    print("win_rate:", round(win_rate,3))
    print("avg_R:", round(avg_R,3))

if __name__ == "__main__":
    df = pd.read_csv("data.csv")
    backtest(df)
