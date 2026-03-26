import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# 🔥 REGIME ENGINE（升級版）
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
# 🔥 STRATEGY 1（TREND）
# =========================
def trend_strategy(row, imbalance):

    if abs(imbalance) < 0.2:
        return "SKIP"

    return "LONG" if imbalance > 0 else "SHORT"


# =========================
# 🔥 STRATEGY 2（RANGE）
# =========================
def range_strategy(row, imbalance):

    if abs(imbalance) < 0.2:
        return "SKIP"

    # 👉 反打
    return "SHORT" if imbalance > 0 else "LONG"


# =========================
# 🔥 STRATEGY ROUTER（核心）
# =========================
def route_strategy(regime, row, imbalance):

    if regime == "TREND":
        return trend_strategy(row, imbalance)

    elif regime == "RANGE":
        return range_strategy(row, imbalance)

    else:
        return "SKIP"


# =========================
# 🔥 ENTRY
# =========================
def get_entry(row, signal, regime):

    high = safe_get(row, "high")
    low = safe_get(row, "low")

    range_ = high - low

    if range_ == 0:
        return safe_get(row, "close")

    ratio = 0.2 if regime == "TREND" else 0.5

    if signal == "LONG":
        return low + range_ * ratio
    else:
        return high - range_ * ratio


# =========================
# 🔥 TP / SL
# =========================
def get_tp_sl(entry, signal, regime):

    R = abs(entry * 0.01)

    tp_mult = 3 if regime == "TREND" else 1.5

    if signal == "LONG":
        return entry + R * tp_mult, entry - R
    else:
        return entry - R * tp_mult, entry + R


# =========================
# 🔥 TRADE
# =========================
def simulate_trade(row, signal, entry, tp, sl):

    high = safe_get(row, "high")
    low = safe_get(row, "low")

    if signal == "LONG":
        if low <= sl:
            return -1
        if high >= tp:
            return +2

    else:
        if high >= sl:
            return -1
        if low <= tp:
            return +2

    return 0


# =========================
# 🔥 BACKTEST
# =========================
def backtest(df):

    wins, losses, skips, breakeven = 0, 0, 0, 0
    pnl_R = []

    for _, row in df.iterrows():

        regime, strength = detect_regime(row)

        liq_above, liq_below, imbalance = calc_liquidity(row)

        signal = route_strategy(regime, row, imbalance)

        if signal == "SKIP":
            skips += 1
            continue

        entry = get_entry(row, signal, regime)
        tp, sl = get_tp_sl(entry, signal, regime)

        result = simulate_trade(row, signal, entry, tp, sl)

        pnl_R.append(result)

        if result > 0:
            wins += 1
        elif result < 0:
            losses += 1
        else:
            breakeven += 1

    total = wins + losses

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "skips": skips,
        "win_rate": round(wins / total, 3) if total else 0,
        "avg_R": round(np.mean(pnl_R), 3) if pnl_R else 0
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

    print("🔥 Steel X V59 (Strategy Router)")
    for k, v in result.items():
        print(f"{k}: {v}")
