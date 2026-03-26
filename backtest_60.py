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
def detect_regime(row):

    open_ = safe_get(row, "open")
    close = safe_get(row, "close")
    high = safe_get(row, "high")
    low = safe_get(row, "low")

    body = abs(close - open_)
    range_ = high - low

    if range_ == 0:
        return "CHOP"

    strength = body / range_

    if strength > 0.6:
        return "TREND"
    elif strength > 0.3:
        return "RANGE"
    else:
        return "CHOP"


# =========================
# LIQUIDITY
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
        return 0

    return (liq_above - liq_below) / total


# =========================
# STRATEGIES
# =========================
def trend_strategy(imbalance):
    return "LONG" if imbalance > 0 else "SHORT"

def range_strategy(imbalance):
    return "SHORT" if imbalance > 0 else "LONG"


# =========================
# CAPITAL ALLOCATOR（核心）
# =========================
class CapitalAllocator:

    def __init__(self):
        self.performance = {
            "TREND": [],
            "RANGE": []
        }

    def update(self, regime, result):
        if regime in self.performance:
            self.performance[regime].append(result)

    def get_weight(self, regime):

        data = self.performance.get(regime, [])

        if len(data) < 10:
            return 1.0  # 初期平均分配

        avg = np.mean(data[-20:])  # 最近20筆

        # 🔥 表現好 → 加權
        if avg > 0:
            return 1.5
        else:
            return 0.5


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

    allocator = CapitalAllocator()

    equity = 100
    history = []

    for _, row in df.iterrows():

        regime = detect_regime(row)

        if regime == "CHOP":
            history.append(equity)
            continue

        imbalance = calc_liquidity(row)

        if abs(imbalance) < 0.2:
            history.append(equity)
            continue

        # 👉 選策略
        if regime == "TREND":
            signal = trend_strategy(imbalance)
        else:
            signal = range_strategy(imbalance)

        result = simulate_trade(row, signal)

        # 👉 資金權重
        weight = allocator.get_weight(regime)

        pnl = result * weight

        equity += pnl

        # 👉 更新策略表現
        allocator.update(regime, result)

        history.append(equity)

    return history


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

    equity_curve = backtest(df)

    print("🔥 Steel X V60 (Capital Allocator)")
    print(f"Final Equity: {equity_curve[-1]:.2f}")
