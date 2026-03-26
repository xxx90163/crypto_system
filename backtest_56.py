import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# 🔥 LIQUIDITY ENGINE（核心）
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
# 🔥 DIRECTION（由流動性決定）
# =========================
def get_signal_from_liquidity(imbalance):

    if imbalance > 0.2:
        return "LONG"
    elif imbalance < -0.2:
        return "SHORT"
    else:
        return "SKIP"


# =========================
# 🔥 ENTRY SOLVER（流動性版）
# =========================
def get_entry(row, signal):

    high = safe_get(row, "high")
    low = safe_get(row, "low")
    close = safe_get(row, "close")

    range_ = high - low

    if range_ == 0:
        return close

    # 👉 不追價：回踩進場
    if signal == "LONG":
        entry = low + range_ * 0.3
    else:
        entry = high - range_ * 0.3

    return entry


# =========================
# 🔥 TP / SL（吃流動性）
# =========================
def get_tp_sl(entry, signal, liq_above, liq_below):

    R = abs(entry * 0.01)  # 動態R

    if signal == "LONG":
        tp = entry + max(R * 2, liq_above * 0.0001)
        sl = entry - R
    else:
        tp = entry - max(R * 2, liq_below * 0.0001)
        sl = entry + R

    return tp, sl


# =========================
# 🔥 TRADE ENGINE
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

        liq_above, liq_below, imbalance = calc_liquidity(row)

        signal = get_signal_from_liquidity(imbalance)

        if signal == "SKIP":
            skips += 1
            continue

        entry = get_entry(row, signal)

        tp, sl = get_tp_sl(entry, signal, liq_above, liq_below)

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

    print("🔥 Steel X V56 (Liquidity × Execution)")
    for k, v in result.items():
        print(f"{k}: {v}")
