# backtest_engine.py

from aip_engine import build_aip


def run_backtest(n=50):

    results = []

    for i in range(n):
        data = build_aip()
        results.append(data)

    return results


def analyze_results(results):

    total = len(results)
    wins = 0
    losses = 0
    skips = 0

    total_pnl = 0
    max_drawdown = 0
    current_drawdown = 0

    for r in results:

        result = r.get("result")
        pnl = r.get("pnl", 0)

        if result == "WIN":
            wins += 1
        elif result == "LOSS":
            losses += 1
        else:
            skips += 1

        total_pnl += pnl

        # 🔥 簡單回撤
        if pnl < 0:
            current_drawdown += pnl
            max_drawdown = min(max_drawdown, current_drawdown)
        else:
            current_drawdown = 0

    win_rate = round(wins / total, 2) if total != 0 else 0
    avg_pnl = round(total_pnl / total, 2) if total != 0 else 0

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "skips": skips,
        "win_rate": win_rate,
        "avg_pnl": avg_pnl,
        "max_drawdown": round(max_drawdown, 2)
    }


if __name__ == "__main__":

    results = run_backtest(100)
    stats = analyze_results(results)

    print("\n💀 Steel X AIP v8 回測結果")
    for k, v in stats.items():
        print(f"{k}: {v}")
