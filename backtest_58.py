import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# 🔥 REGIME（升級）
# =========================
def detect_regime(row):

    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    high = safe_get(row, "high")
    low = safe_get(row, "low")

    body = abs(close - open_)
    range_ = high - low

    if range_ == 0:
        return "UNKNOWN", 0

    strength = body / range_

    if strength > 0.6:
        return "TREND", strength
    else:
        return "RANGE", strength


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
# 🔥 ADAPTIVE THRESHOLD
# =========================
def adaptive_threshold(row):

    range_ = safe_get(row, "high") - safe_get(row, "low")
    price = safe_get(row, "close")

    vol = range_ / (price + 1e-9)

    # 👉 波動大 → 門檻高
    if vol > 0.02:
        return 0.3
    elif vol > 0.01:
        return 0.2
    else:
        return 0.15


# =========================
# 🔥 ABSORPTION（新）
# =========================
def detect_absorption(row):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")

    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    body = abs(close - open_)

    if body == 0:
        return 0

    # 👉 吃單判斷
    absorption = (upper_wick + lower_wick) / body

    return absorption


# =========================
# 🔥 STRUCTURE BIAS
# =========================
def structure_bias(regime, strength):

    if regime == "TREND":
        return 1 + strength
    else:
        return 1 - strength


# =========================
# 🔥 SIGNAL（自適應）
# =========================
def generate_signal(regime, imbalance, threshold, bias, absorption):

    if abs(imbalance) < threshold:
        return "SKIP"

    # 👉 absorption 太高 → 不做
    if absorption > 2:
        return "SKIP"

    # TREND
    if regime == "TREND":
        return "LONG" if imbalance > 0 else "SHORT"

    # RANGE（反打）
    else:
        return "SHORT" if imbalance > 0 else "LONG"


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

        threshold = adaptive_threshold(row)

        absorption = detect_absorption(row)

        bias = structure_bias(regime, strength)

        signal = generate_signal(regime, imbalance, threshold, bias, absorption)

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

    print("🔥 Steel X V58 (Adaptive Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
