import pandas as pd
import numpy as np

# =========================
# SAFE GET
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# REGIME
# =========================
def get_regime(row):
    return "TREND" if safe_get(row, "close") > safe_get(row, "open") else "RANGE"


# =========================
# SIGNAL
# =========================
def generate_signal(row):
    return "LONG" if get_regime(row) == "TREND" else "SHORT"


# =========================
# ENTRY SOLVER（簡化版）
# =========================
def get_entry_sl_tp(row, signal):

    price = safe_get(row, "close")
    atr = safe_get(row, "atr", 5)  # fallback

    R = atr

    if signal == "LONG":
        entry = price
        sl = entry - R
        tp = entry + 2 * R
    else:
        entry = price
        sl = entry + R
        tp = entry - 2 * R

    return entry, sl, tp, R


# =========================
# TRADE ENGINE（核心）
# =========================
def simulate_trade(row, signal):

    high = safe_get(row, "high")
    low = safe_get(row, "low")

    entry, sl, tp, R = get_entry_sl_tp(row, signal)

    # LONG
    if signal == "LONG":

        if low <= sl:
            return -1  # -1R

        if high >= tp:
            return +2  # +2R

    # SHORT
    else:

        if high >= sl:
            return -1

        if low <= tp:
            return +2

    return 0  # 沒觸發


# =========================
# BACKTEST
# =========================
def backtest(df):

    wins, losses, breakeven = 0, 0, 0
    pnl_R = []

    for _, row in df.iterrows():

        signal = generate_signal(row)

        result = simulate_trade(row, signal)

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
        "win_rate": round(wins / total, 3) if total else 0,
        "avg_R": round(np.mean(pnl_R), 3)
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
        "atr": np.random.rand(1000) * 5 + 1
    })

    result = backtest(df)

    print("🔥 Steel X V55 (Execution Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
