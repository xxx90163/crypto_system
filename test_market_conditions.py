import random

# =========================
# 🔧 模擬市場資料生成器
# =========================

def generate_trend_up(n=100):
    price = 70000
    data = []
    for i in range(n):
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
    for i in range(n):
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
    for i in range(n):
        change = random.randint(-150, 150)
        open_ = price
        close = price + change
        high = max(open_, close) + random.randint(0, 50)
        low = min(open_, close) - random.randint(0, 50)
        data.append({"open": open_, "high": high, "low": low, "close": close})
        price = close
    return data


# =========================
# 🧠 你的策略（簡化版）
# =========================

def generate_signal(prev, curr):
    momentum = curr["close"] - prev["close"]

    if momentum > 100:
        return "LONG"
    elif momentum < -100:
        return "SHORT"
    else:
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
# 🧪 回測核心
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
# 🧠 評估策略
# =========================

def evaluate(results):
    print("\n📊 市場測試結果\n")

    for name, res in results.items():
        print(f"=== {name} ===")
        for k, v in res.items():
            print(f"{k}: {v}")
        print()

    # 判斷
    up = results["TREND_UP"]["win_rate"]
    down = results["TREND_DOWN"]["win_rate"]
    range_ = results["RANGE"]["win_rate"]

    print("🧠 策略判斷：")

    if up > 0.7 and down < 0.3:
        print("👉 偏多策略（只吃上漲）")
    elif down > 0.7 and up < 0.3:
        print("👉 偏空策略（只吃下跌）")
    elif 0.4 < range_ < 0.6:
        print("👉 震盪策略（較平衡）")
    else:
        print("👉 混合或不穩定策略")

    print("\n⚠ 建議：如果只在一種市場賺 → 不可實盤")


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
