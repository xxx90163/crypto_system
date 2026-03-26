import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# 🔥 REGIME ENGINE
# =========================
def detect_regime(row):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")

    range_ = high - low
    body = abs(close - open_)

    if range_ == 0:
        return "UNKNOWN"

    ratio = body / range_

    # 👉 強趨勢
    if ratio > 0.6:
        return "TREND"

    # 👉 震盪
    return "RANGE"


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
        return liq_above, liq_below, 0

    imbalance = (liq_above - liq_below) / total

    return liq_above, liq_below, imbalance


# =========================
# 🔥 SIGNAL（依 regime）
# =========================
def get_signal(regime, imbalance):

    # ===== TREND =====
    if regime == "TREND":
        if imbalance > 0.2:
            return "LONG"
        elif imbalance < -0.2:
            return "SHORT"

    # ===== RANGE（反打）=====
    elif regime == "RANGE":
        if imbalance > 0.2:
            return "SHORT"
        elif imbalance < -0.2:
            return "LONG"

    return "SKIP"


# =========================
# 🔥 ENTRY（依 regime）
# =========================
def get_entry(row, signal, regime):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    close = safe_get(row, "close")

    range_ = high - low

    if range_ == 0:
        return close

    # TREND → 淺回踩
    if regime == "TREND":
        pb = 0.2
    else:
        pb = 0.5

    if signal == "LONG":
        return low + range_ * pb
    else:
        return high - range_ * pb


# =========================
# 🔥 TP / SL（依 regime）
# =========================
def get_tp_sl(entry, signal, liq_above, liq_below, regime):

    base_R = entry * 0.01

    if regime == "TREND":
        R = base_R * 1.2
    else:
        R = base_R * 0.8

    if signal == "LONG":
        tp = entry + max(R * 2, liq_above * 0.0001)
        sl = entry - R
    else:
        tp = entry - max(R * 2, liq_below * 0.0001)
        sl = entry + R

    return tp, sl


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

    wins, losses, breakeven, skips = 0, 0, 0, 0
    pnl_R = []

    for _, row in df.iterrows():

        regime = detect_regime(row)

        liq_above, liq_below, imbalance = calc_liquidity(row)

        signal = get_signal(regime, imbalance)

        if signal == "SKIP":
            skips += 1
            continue

        entry = get_entry(row, signal, regime)

        tp, sl = get_tp_sl(entry, signal, liq_above, liq_below, regime)

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

    print("🔥 Steel X V57 (Regime × Liquidity)")
    for k, v in result.items():
        print(f"{k}: {v}")
