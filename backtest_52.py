import pandas as pd
import numpy as np

# =========================
# SAFE GET（避免 KeyError）
# =========================
def safe_get(row, key, default=0):
    return row[key] if key in row else default


# =========================
# REAL + PROXY LIQUIDITY
# =========================
def calc_liquidity(row):
    """
    優先使用真實流動性資料
    fallback → proxy（K線推估）
    """

    liq_above = safe_get(row, "liq_above", None)
    liq_below = safe_get(row, "liq_below", None)

    # =====================
    # ✅ REAL DATA MODE
    # =====================
    if liq_above is not None and liq_below is not None:
        return liq_above, liq_below, "REAL"

    # =====================
    # ⚠️ PROXY MODE（fallback）
    # =====================
    high = safe_get(row, "high", 0)
    low = safe_get(row, "low", 0)
    open_ = safe_get(row, "open", 0)
    close = safe_get(row, "close", 0)
    volume = safe_get(row, "volume", 1)

    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    liq_above = upper_wick * volume
    liq_below = lower_wick * volume

    return liq_above, liq_below, "PROXY"


# =========================
# REGIME（容錯版）
# =========================
def get_regime(row):
    if "regime" in row:
        return row["regime"]

    # fallback：用價格動能判斷
    open_ = safe_get(row, "open")
    close = safe_get(row, "close")

    if close > open_:
        return "TREND"
    else:
        return "RANGE"


# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(row):
    regime = get_regime(row)

    if regime == "TREND":
        return "LONG"
    else:
        return "SHORT"


# =========================
# LIQUIDITY FILTER（核心）
# =========================
def liquidity_filter(liq_above, liq_below, threshold=50):

    strength = abs(liq_above - liq_below)

    if strength < threshold:
        return False, strength

    return True, strength


# =========================
# BACKTEST
# =========================
def backtest(df):

    wins = 0
    losses = 0
    skips = 0
    pnl_list = []

    for i, row in df.iterrows():

        liq_above, liq_below, mode = calc_liquidity(row)

        allow, strength = liquidity_filter(liq_above, liq_below)

        if not allow:
            skips += 1
            continue

        signal = generate_signal(row)

        # =====================
        # 模擬 pnl（簡化版）
        # =====================
        move = np.random.choice([-80, 150])

        if signal == "LONG":
            pnl = move
        else:
            pnl = -move

        pnl_list.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    win_rate = wins / total if total > 0 else 0
    avg_pnl = np.mean(pnl_list) if pnl_list else 0

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "skips": skips,
        "win_rate": round(win_rate, 3),
        "avg_pnl": round(avg_pnl, 2),
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":

    # ===== 測試資料（可換成你CSV）=====
    df = pd.DataFrame({
        "open": np.random.rand(1000) * 100,
        "close": np.random.rand(1000) * 100,
        "high": np.random.rand(1000) * 100,
        "low": np.random.rand(1000) * 100,
        "volume": np.random.rand(1000) * 1000,

        # 👉 這裡可切換 REAL / PROXY
        # "liq_above": np.random.rand(1000) * 500,
        # "liq_below": np.random.rand(1000) * 500,
    })

    result = backtest(df)

    print("🔥 Steel X V52 (Real Liquidity Engine)")
    for k, v in result.items():
        print(f"{k}: {v}")
