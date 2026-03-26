import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# 🔥 REGIME
# =========================
def detect_regime(row):

    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    high = safe_get(row, "high")
    low = safe_get(row, "low")

    body = abs(close - open_)
    range_ = high - low

    if range_ == 0:
        return "CHOP", 0

    strength = body / range_

    if strength > 0.6:
        return "TREND", strength
    elif strength > 0.3:
        return "RANGE", strength
    else:
        return "CHOP", strength


# =========================
# 🔥 LIQUIDITY
# =========================
def calc_liquidity(row):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    volume = safe_get(row, "volume", 1)

    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    liq_above = upper_wick * volume
    liq_below = lower_wick * volume

    total = liq_above + liq_below

    if total == 0:
        return 0, 0, 0

    imbalance = (liq_above - liq_below) / total

    return liq_above, liq_below, imbalance


# =========================
# 🔥 BREAK STRUCTURE
# =========================
def break_structure(row):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")

    # 上破 / 下破
    if close > high * 0.995:
        return "BREAK_UP"
    elif close < low * 1.005:
        return "BREAK_DOWN"
    else:
        return "NONE"


# =========================
# 🔥 TRIGGER ENGINE（核心）
# =========================
def trigger_engine(row):

    regime, strength = detect_regime(row)
    liq_above, liq_below, imbalance = calc_liquidity(row)
    structure = break_structure(row)

    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    high = safe_get(row, "high")
    low = safe_get(row, "low")

    body = abs(close - open_)
    range_ = high - low

    if range_ == 0:
        return False

    body_ratio = body / range_

    # =========================
    # 🔥 四大條件（全部要過）
    # =========================

    # 1️⃣ 流動性
    cond_liq = abs(imbalance) > 0.3

    # 2️⃣ 動能
    cond_momentum = body_ratio > 0.5

    # 3️⃣ 結構
    cond_structure = structure != "NONE"

    # 4️⃣ 非亂盤
    cond_regime = regime != "CHOP"

    return cond_liq and cond_momentum and cond_structure and cond_regime


# =========================
# STRATEGY
# =========================
def get_signal(row, imbalance, regime):

    if regime == "TREND":
        return "LONG" if imbalance > 0 else "SHORT"

    elif regime == "RANGE":
        return "SHORT" if imbalance > 0 else "LONG"

    return "SKIP"


# =========================
# TRADE
# =========================
def simulate_trade(row, signal):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    close = safe_get(row, "close")

    R = abs(close * 0.01)

    if signal == "LONG":
        if low <= close - R:
            return -1
        if high >= close + 2*R:
            return +2

    else:
        if high >= close + R:
            return -1
        if low <= close - 2*R:
            return +2

    return 0


# =========================
# BACKTEST
# =========================
def backtest(df):

    wins, losses, skips = 0, 0, 0
    pnl = []

    for _, row in df.iterrows():

        if not trigger_engine(row):
            skips += 1
            continue

        regime, _ = detect_regime(row)
        _, _, imbalance = calc_liquidity(row)

        if abs(imbalance) < 0.2:
            skips += 1
            continue

        signal = get_signal(row, imbalance, regime)

        result = simulate_trade(row, signal)

        pnl.append(result)

        if result > 0:
            wins += 1
        elif result < 0:
            losses += 1

    total = wins + losses

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "skips": skips,
        "win_rate": round(wins / total, 3) if total else 0,
        "avg_R": round(np.mean(pnl), 3) if pnl else 0
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":

    df = pd.DataFrame({
        "open": np.random.rand(1000) * 100,
        "close": np.random.rand(1000) * 100,
        "high": np.random.rand(1000) * 100 + 5,
        "low": np.random.rand(1000) * 100 - 5,
        "volume": np.random.rand(1000) * 1000
    })

    result = backtest(df)

    print("🔥 Steel X V61 (Trigger Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
