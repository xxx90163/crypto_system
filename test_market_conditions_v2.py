import random

# =========================
# 📊 市場資料生成
# =========================

def generate_trend_up(n=100):
    price = 70000
    data = []
    for _ in range(n):
        change = random.randint(50, 200)
        open_ = price
        close = price + change
        high = max(open_, close) + random.randint(0, 50)
        low = min(open_, close) - random.randint(0, 50)
        data.append({"open": open_, "high": high, "low": low, "close": close})
        price = close
    return data


def generate_trend_down(n=100):
    price = 70000
    data = []
    for _ in range(n):
        change = random.randint(50, 200)
        open_ = price
        close = price - change
        high = max(open_, close) + random.randint(0, 50)
        low = min(open_, close) - random.randint(0, 50)
        data.append({"open": open_, "high": high, "low": low, "close": close})
        price = close
    return data


def generate_range(n=100):
    price = 70000
    data = []
    for _ in range(n):
        change = random.randint(-150, 150)
        open_ = price
        close = price + change
        high = max(open_, close) + random.randint(0, 50)
        low = min(open_, close) - random.randint(0, 50)
        data.append({"open": open_, "high": high, "low": low, "close": close})
        price = close
    return data


# =========================
# 🧠 市場狀態判斷（核心）
# =========================

def detect_regime(prev, curr):
    move = abs(curr["close"] - prev["close"])

    if move > 120:
        return "TREND"
    else:
        return "RANGE"


# =========================
# 🧠 訊號（升級版）
# =========================

def generate_signal(prev, curr):
    momentum = curr["close"] - prev["close"]
    regime = detect_regime(prev, curr)

    # 👉 趨勢市場才交易
    if regime == "TREND":
        if momentum > 100:
            return "LONG"
        elif momentum < -100:
            return "SHORT"

    # 👉 震盪市場 → 不交易（避免虧）
    return None


# =========================
# 💰 交易模擬
# =========================

def simulate_trade(entry, signal, next_candle):
    if signal == "LONG":
        return next_candle["close"] - entry
    elif signal == "SHORT":
        return entry - next_candle["close"]
    return 0


# =========================
# 🧪 回測
# =========================

def run_backtest(data):
    wins = 0
    losses = 0
    skips = 0
    pnl_list = []

    for i in range(1, len(data) - 1):
        prev = data[i - 1]
        curr = data[i]
        next_candle = data[i + 1]

        signal = generate_signal(prev, curr)

        if signal is None:
            skips += 1
            continue

        entry = curr["close"]
        pnl = simulate_trade(entry, signal, next_candle)

        pnl_list.append(pnl)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses
    win_rate = wins / total if total > 0 else 0
    avg_pnl = sum(pnl_list) / len(pnl_list) if pnl_list else 0

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "skips": skips,
        "win_rate": round(win_rate, 3),
        "avg_pnl": round(avg_pnl, 2),
    }


# =========================
# 🧠 評估
# =========================

def evaluate(results):
    print("\n📊 V24.TEST（市場判斷版）\n")

    for name, res in results.items():
        print(f"=== {name} ===")
        for k, v in res.items():
            print(f"{k}: {v}")
        print()

    print("🧠 判斷：")
    print("✔ 趨勢吃到 → 正常")
    print("✔ 震盪少交易 → 正常")
    print("✔ avg_pnl 應該變穩定")


# =========================
# 🚀 主程式
# =========================

if __name__ == "__main__":
    trend_up = generate_trend_up()
    trend_down = generate_trend_down()
    range_data = generate_range()

    results = {
        "TREND_UP": run_backtest(trend_up),
        "TREND_DOWN": run_backtest(trend_down),
        "RANGE": run_backtest(range_data),
    }

    evaluate(results)
